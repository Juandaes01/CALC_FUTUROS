from datetime import datetime
HOY= datetime.now() 

def precioFuturo(precio_actual, tasa_interes,vencimiento, nominales_dividendos,Fechas_exdiv,Fechas_pagos):
       
    # Calcular el tiempo hasta el vencimiento
    fv = datetime.strptime(vencimiento, '%Y-%m-%d %H:%M:%S')
    fv = fv.strftime('%Y-%m-%d')
    fecha_vencimiento = datetime.strptime(fv, '%Y-%m-%d')
    tiempo = (fecha_vencimiento - HOY).days +1  # Tiempo en días
    valor_presente_dividendos = 0
    for i, fechaexdv in enumerate(Fechas_exdiv):
        if fechaexdv == 'No tiene':
            valor_presente_dividendos += 0
        else:
            fechaexdv= datetime.strptime(fechaexdv, '%Y-%m-%d')
            if (fechaexdv>HOY)&(fechaexdv<fecha_vencimiento):
                Fecha_pago= datetime.strptime(Fechas_pagos[i], '%Y-%m-%d')
                dias_dvdo= (Fecha_pago - HOY).days +1  # Tiempo en días
                nominal_dividendo= nominales_dividendos[i]
                valor_presente_dividendos += nominal_dividendo/((1+tasa_interes/100)**(dias_dvdo/365))

    # Calcular el precio futuro
    return (precio_actual - valor_presente_dividendos) * ((1 + tasa_interes / 100) ** (tiempo / 365))
