import argparse
import math
import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Targets de marcas por CECO (metas de negocio - actualizar si cambian)
METAS_MARCAS = {
    'GRAN PLAZA ALCARAVAN': 65,
    'GRAN PLAZA BOSA': 99,
    'GRAN PLAZA DEL SOL': 114,
    'GRAN PLAZA ENSUEÑO': 122,
    'GRAN PLAZA FLORENCIA': 87,
    'GRAN PLAZA IPIALES': 91,
    'GRAN PLAZA SAN ANTONIO': 63,
    'GRAN PLAZA SOACHA': 103,
}

METAS_MARCAS_FOCO = {
    'GRAN PLAZA ALCARAVAN': 28,
    'GRAN PLAZA BOSA': 30,
    'GRAN PLAZA DEL SOL': 31,
    'GRAN PLAZA ENSUEÑO': 34,
    'GRAN PLAZA FLORENCIA': 30,
    'GRAN PLAZA IPIALES': 31,
    'GRAN PLAZA SAN ANTONIO': 27,
    'GRAN PLAZA SOACHA': 29,
}


def _clean(val):
    """Convierte NaN/inf a None para serialización JSON."""
    if val is None:
        return None
    try:
        if math.isnan(val) or math.isinf(val):
            return None
    except (TypeError, ValueError):
        pass
    return val


def _clean_records(records):
    """Limpia todos los valores NaN en una lista de dicts."""
    return [{k: _clean(v) for k, v in row.items()} for row in records]


def cargar_ventas(path):
    return {
        'datos':       pd.read_excel(path, sheet_name='Datos Originales'),
        'resumen':     pd.read_excel(path, sheet_name='Tabla suma ventas'),
        'marcas':      pd.read_excel(path, sheet_name='Marcas totales'),
        'marcas_foco': pd.read_excel(path, sheet_name='Marcas totales FOCO'),
        'mismas':      pd.read_excel(path, sheet_name='Mismas Marcas'),
    }


def cargar_trafico(path):
    df = pd.read_excel(path, sheet_name='Tráfico (Base de datos)',
                       usecols=['CECO', 'FECHA', 'DIA', 'TRÁFICO', 'Anterior (Retail Dia/Día)'])
    df['FECHA'] = pd.to_datetime(df['FECHA'])
    df['año'] = df['FECHA'].dt.year
    df['semana_iso'] = df['FECHA'].dt.isocalendar().week.astype(int)
    return df


def _build_resumen(df):
    result = df[['CECO', 'Semana', 'Venta diaria', 'Venta Mismo Dia Anterior', 'Ppto']].rename(columns={
        'Venta diaria': 'venta',
        'Venta Mismo Dia Anterior': 'venta_ant',
        'Ppto': 'ppto',
    }).sort_values(['Semana', 'CECO']).reset_index(drop=True)
    # Reordenar columnas para coincidir con estructura original: Semana, CECO, venta, venta_ant, ppto
    result = result[['Semana', 'CECO', 'venta', 'venta_ant', 'ppto']]
    return _clean_records(result.to_dict(orient='records'))


def _build_por_marca(df):
    # "Datos Originales" tiene filas diarias; agregar a totales semanales
    grouped = df.groupby(['CECO', 'Marca', 'Categoría', 'Semana', 'Marca Foco'], as_index=False).agg(
        venta=('Venta diaria', 'sum'),
        venta_ant=('Venta Mismo Dia Anterior', 'sum'),
        ppto=('Ppto', 'sum'),
        dias_con_venta=('Venta diaria', lambda x: (x > 0).sum()),
    ).rename(columns={
        'Categoría': 'Categoria',
        'Marca Foco': 'MarcaFoco',
    })
    return _clean_records(grouped.to_dict(orient='records'))


def _build_por_categoria(df):
    grouped = df.groupby(['Semana', 'CECO', 'Categoría'], as_index=False).agg(
        venta=('Venta diaria', 'sum'),
        venta_ant=('Venta Mismo Dia Anterior', 'sum'),
        ppto=('Ppto', 'sum'),
    ).rename(columns={'Categoría': 'Categoria'})
    return _clean_records(grouped.to_dict(orient='records'))


def _build_pivot(df, count_col):
    """Convierte un DataFrame CECO/Semana/valor a {ceco: {semana_str: valor}}."""
    result = {}
    for _, row in df.iterrows():
        ceco = row['CECO']
        semana = str(int(row['Semana']))
        val = row[count_col]
        val = int(val) if not (isinstance(val, float) and math.isnan(val)) else 0
        if ceco not in result:
            result[ceco] = {}
        result[ceco][semana] = val
    return result


def _build_mismas_total(df):
    """Suma de mismas_marcas por semana (todos los CECOs)."""
    totals = df.groupby('Semana')['Total Mismas Marcas'].sum()
    return {str(int(k)): int(v) for k, v in totals.items()}


def _build_trafico(df_trafico, semanas):
    # Filtrar al año más reciente que tenga datos para las semanas de ventas
    años_con_datos = df_trafico[df_trafico['semana_iso'].isin(semanas)]['año'].unique()
    año_max = int(max(años_con_datos))
    df = df_trafico[(df_trafico['año'] == año_max) & (df_trafico['semana_iso'].isin(semanas))].copy()

    col_ant = 'Anterior (Retail Dia/Día)'

    # trafico_por_semana: total por semana (todos los CECOs)
    tps = df.groupby('semana_iso').agg(
        trafico=(  'TRÁFICO', 'sum'),
        trafico_ant=(col_ant, 'sum'),
    ).reset_index()
    trafico_por_semana = [
        {'semana': int(r['semana_iso']), 'trafico': _clean(r['trafico']), 'trafico_ant': _clean(r['trafico_ant'])}
        for _, r in tps.iterrows()
    ]

    # trafico_por_semana_ceco: total por semana y CECO
    tpsc = df.groupby(['semana_iso', 'CECO']).agg(
        trafico=('TRÁFICO', 'sum'),
        trafico_ant=(col_ant, 'sum'),
    ).reset_index()
    trafico_por_semana_ceco = [
        {
            'semana': int(r['semana_iso']),
            'ceco': r['CECO'],
            'trafico': _clean(r['trafico']),
            'trafico_ant': _clean(r['trafico_ant']),
        }
        for _, r in tpsc.iterrows()
    ]

    # trafico_dias_extremos: día con más y menos tráfico por semana (global, suma todos los CECOs)
    trafico_dias_extremos = {}
    for semana in semanas:
        week_df = df[df['semana_iso'] == semana]
        if week_df.empty:
            continue
        daily = week_df.groupby('DIA')['TRÁFICO'].sum()
        max_dia = daily.idxmax()
        min_dia = daily.idxmin()
        trafico_dias_extremos[str(semana)] = {
            'dia_max': max_dia,
            'trafico_max': float(daily[max_dia]),
            'dia_min': min_dia,
            'trafico_min': float(daily[min_dia]),
        }

    return {
        'trafico_por_semana': trafico_por_semana,
        'trafico_por_semana_ceco': trafico_por_semana_ceco,
        'trafico_dias_extremos': trafico_dias_extremos,
    }


def construir_D(path_ventas, path_trafico):
    v = cargar_ventas(path_ventas)
    t = cargar_trafico(path_trafico)

    datos = v['datos']
    semanas = sorted(datos['Semana'].dropna().unique().astype(int).tolist())
    cecos = sorted(datos['CECO'].dropna().unique().tolist())

    D = {
        'cecos':                  cecos,
        'semanas':                semanas,
        'ultima_semana':          int(datos['Semana'].max()),
        'categorias':             datos['Categoría'].dropna().unique().tolist(),
        'total_registros':        int(len(datos)),
        'resumen':                _build_resumen(v['resumen']),
        'por_marca':              _build_por_marca(datos),
        'por_categoria':          _build_por_categoria(datos),
        'marcas_totales':         _build_pivot(v['marcas'],       'Total Marcas con Venta diaria actual'),
        'marcas_foco_real':       _build_pivot(v['marcas_foco'],  'Total Marcas FOCO con Venta diaria actual'),
        'mismas_marcas':          _build_pivot(v['mismas'],       'Total Mismas Marcas'),
        'mismas_marcas_total':    _build_mismas_total(v['mismas']),
        'metas_marcas':           METAS_MARCAS,
        'meta_total_marcas':      sum(METAS_MARCAS.values()),
        'metas_marcas_foco':      METAS_MARCAS_FOCO,
        'meta_total_marcas_foco': sum(METAS_MARCAS_FOCO.values()),
        **_build_trafico(t, semanas),
    }

    return D


def render_html(D, template_path, output_path):
    template_dir = os.path.dirname(os.path.abspath(template_path))
    template_file = os.path.basename(template_path)
    env = Environment(loader=FileSystemLoader(template_dir))
    tpl = env.get_template(template_file)
    html = tpl.render(data=D)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    
    # C:\Users\MarianaGomezPiedrahi\Pactia\Equipo Datos - Automatizaciones\Pruebas Mariana\Pruebas Mariana\reporte venta diaria semanal.xlsx
    # C:\Users\MarianaGomezPiedrahi\Pactia\Equipo Datos - Automatizaciones\Pruebas Mariana\Pruebas Mariana\trafico.xlsx
    # C:\Users\MarianaGomezPiedrahi\Pactia\Equipo Datos - Automatizaciones\Pruebas Mariana\Pruebas Mariana\dashboard_template.html
    
    parser = argparse.ArgumentParser(description='Generador de Dashboard Gran Plaza')
    parser.add_argument('trafico', help='Ruta al archivo trafico.xlsx')
    parser.add_argument('ventas', help='Ruta al archivo de reporte de ventas .xlsx')
    parser.add_argument('--output', default='dashboard.html', help='Nombre del archivo HTML de salida')
    parser.add_argument('--template', default='dashboard_template.html', help='Ruta al template HTML')
    args = parser.parse_args()

    print(f"Cargando datos:")
    print(f"  Tráfico : {args.trafico}")
    print(f"  Ventas  : {args.ventas}")

    D = construir_D(args.ventas, args.trafico)

    print(f"\nDatos procesados:")
    print(f"  Semanas  : {D['semanas']}")
    print(f"  CECOs    : {len(D['cecos'])} centros")
    print(f"  Registros: {D['total_registros']} marcas")

    output_path = args.output
    render_html(D, args.template, output_path)
    print(f"\n✓ Dashboard generado: {output_path}")


if __name__ == '__main__':
    main()
