# Sistema de Registro (Logging) para Cierre-Caja-Tomasso

Este documento explica cómo usar el sistema de registro (logging) implementado para el proyecto Cierre-Caja-Tomasso. El sistema permite un seguimiento detallado de las operaciones, rendimiento y errores.

## Índice

1. [Integración del Sistema](#integración-del-sistema)
2. [Buenas Prácticas](#buenas-prácticas)
3. [Ejemplos de Uso](#ejemplos-de-uso)
4. [Acceso e Interpretación de Logs](#acceso-e-interpretación-de-logs)
5. [Monitoreo de Rendimiento](#monitoreo-de-rendimiento)

## Integración del Sistema

### Importación Básica

Para comenzar a utilizar el sistema de logging en tu código, simplemente importa el módulo `logger`:

```python
import sys
import os

# Asegurar que src está en el path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Importar el logger
import logger
```

### Funciones Básicas de Logging

El módulo proporciona varias funciones para registrar diferentes tipos de mensajes:

```python
# Mensajes informativos
logger.info("Operación iniciada")

# Mensajes de depuración (detalles adicionales)
logger.debug("Procesando item #1234")

# Advertencias
logger.warning("Caché lleno, limpiando entradas antiguas")

# Errores (no críticos)
logger.error("No se pudo procesar el pedido #5678")

# Errores críticos (afectan al sistema)
logger.critical("Conexión a base de datos perdida")

# Registro de excepciones con stack trace
try:
    # Código que podría fallar
    resultado = funcion_problematica()
except Exception as e:
    logger.log_exception(e, "Error procesando datos")
```

### Medición de Rendimiento

Para medir el rendimiento de operaciones:

```python
# Método 1: Decorador para funciones completas
from logger import measure_performance

@measure_performance
def mi_funcion_importante():
    # Código a medir...
    pass

# Método 2: Medición manual para bloques de código
timer = logger.start_timer("operacion_importante")
try:
    # Código a medir...
    resultado = hacer_algo_complejo()
finally:
    logger.stop_timer(timer, f"Detalles: {resultado}")
```

### Loggers Especializados

Para MercadoPago y Rappi, se ofrecen loggers especializados:

```python
from logger import MercadoPagoLogger, RappiLogger

# Para MercadoPago
timer = MercadoPagoLogger.log_operation_start("sumar_transferencias", fecha)
try:
    # Código de operación...
    resultado = procesar_transferencias()
    MercadoPagoLogger.log_operation_complete(timer, resultado)
except Exception as e:
    MercadoPagoLogger.log_error_pedido("ID-12345", str(e))
```

## Buenas Prácticas

### Uso Adecuado de Niveles de Log

- **DEBUG**: Información detallada, útil durante el desarrollo
- **INFO**: Confirmación de que las cosas funcionan según lo esperado
- **WARNING**: Indicación de que algo inesperado sucedió pero el programa sigue funcionando
- **ERROR**: Debido a un problema más grave, el programa no pudo realizar alguna función
- **CRITICAL**: Error grave que impide que el programa continúe funcionando

### Recomendaciones Generales

1. **Información Contextual**: Incluye siempre información contextual relevante (IDs, fechas, etc.)
    ```python
    logger.error(f"Error procesando pedido {pedido_id} para fecha {fecha}")
    ```

2. **Evita Verbosidad Excesiva**: No registres información sensible o innecesaria
    ```python
    # MAL: Información sensible o excesiva
    logger.debug(f"Contraseña: {password}")
    
    # BIEN: Información relevante sin datos sensibles
    logger.debug(f"Autenticación realizada para usuario: {username}")
    ```

3. **Usa Categorías Consistentes**: Organiza los mensajes por componente o funcionalidad
    ```python
    logger.info("MercadoPago - Iniciando procesamiento")
    logger.info("Rappi - Iniciando procesamiento")
    ```

4. **Nivel Correcto**: Usa el nivel apropiado para cada mensaje
    ```python
    # No usar error para mensajes informativos
    logger.error("Procesamiento iniciado")  # MAL
    logger.info("Procesamiento iniciado")   # BIEN
    ```

## Ejemplos de Uso

### Registro de Operaciones Normales

```python
def procesar_pedido(pedido_id):
    logger.info(f"Iniciando procesamiento de pedido {pedido_id}")
    
    # Obtener detalles
    logger.debug(f"Obteniendo detalles para pedido {pedido_id}")
    
    # Procesamiento exitoso
    logger.info(f"Pedido {pedido_id} procesado exitosamente")
```

### Manejo de Errores

```python
def conectar_api():
    try:
        # Intentar conexión
        logger.debug("Conectando a API de MercadoPago")
        
        if not conexion_exitosa:
            logger.warning("Conexión a API inestable, reintentando...")
            # Reintentar
            
        if error_permanente:
            logger.error("No se pudo establecer conexión después de 3 intentos")
            return False
            
    except Exception as e:
        logger.log_exception(e, "Error inesperado en conexión API")
        return False
        
    return True
```

### Medición de Rendimiento

```python
def procesar_datos_completos(fecha):
    # Medir operación completa
    timer_global = logger.start_timer("procesamiento_diario")
    
    try:
        # Medir suboperación 1
        timer1 = logger.start_timer("procesar_mercadopago")
        resultado1 = procesar_mercadopago(fecha)
        logger.stop_timer(timer1, f"Resultados: {len(resultado1)} items")
        
        # Medir suboperación 2
        timer2 = logger.start_timer("procesar_rappi")
        resultado2 = procesar_rappi(fecha)
        logger.stop_timer(timer2, f"Resultados: {len(resultado2)} items")
        
        # Resultado final
        total = combinar_resultados(resultado1, resultado2)
        logger.info(f"Procesamiento completado, total: {total}")
        
    finally:
        # Siempre registrar tiempo total
        logger.stop_timer(timer_global)
```

## Acceso e Interpretación de Logs

### Ubicación de Archivos de Log

Los logs se almacenan en la carpeta `logs/` del proyecto:

- `logs/tomasso.log`: Registro general
- `logs/errors/error.log`: Errores y excepciones
- `logs/performance/performance.log`: Métricas de rendimiento

### Formato de los Logs

Los logs tienen un formato estándar que incluye:

```
2025-04-15 00:58:01,431 [INFO] MercadoPago.py:45 - Iniciando procesamiento para fecha 2025-04-15
```

- Fecha y hora
- Nivel de log ([INFO], [ERROR], etc.)
- Archivo y línea (para logs detallados)
- Mensaje

### Rotación de Logs

Los archivos de log rotan automáticamente cada día, y se mantienen:

- Logs generales: 30 días
- Logs de error: 60 días
- Logs de rendimiento: 30 días

### Recomendaciones para Análisis

- Usa herramientas como `grep` para buscar patrones específicos:
  ```bash
  grep "ERROR" logs/tomasso.log
  grep "Timeout" logs/errors/error.log
  ```

- Analiza tendencias de rendimiento con:
  ```bash
  grep "MercadoPago.sumar_pedido" logs/performance/performance.log | awk '{print $1, $2, $5}'
  ```

## Monitoreo de Rendimiento

### Indicadores Clave

El sistema registra automáticamente:

1. **Tiempo de ejecución**: Duración de operaciones en segundos
2. **Consumo de memoria**: Uso de memoria en MB
3. **Operaciones por segundo**: Tasa de procesamiento

### Interpretación de Métricas

Ejemplo de entrada en el log de rendimiento:

```
2025-04-15 00:58:01,431 [PERF] MercadoPago.sumar_pedido completado en 3.4521s - Memoria: 24.5MB, Pedidos: 15
```

Esta entrada indica:
- La operación `sumar_pedido` tomó 3.45 segundos
- Consumió 24.5 MB de memoria
- Procesó 15 pedidos

### Detección de Problemas de Rendimiento

- **Operaciones lentas**: Busca en los logs de rendimiento cualquier operación que tome más de 5 segundos.
- **Consumo excesivo de memoria**: Operaciones que usen más de 300MB.
- **Tasas bajas de procesamiento**: Menos de 1 operación por segundo en funciones críticas.

### Optimización Basada en Logs

1. Identifica las operaciones más lentas:
   ```bash
   grep -r "completado en" logs/performance/ | sort -k5 -n -r | head -10
   ```

2. Busca patrones en errores:
   ```bash
   grep -r "Error en" logs/errors/ | cut -d':' -f3 | sort | uniq -c | sort -nr
   ```

3. Monitorea tendencias a lo largo del tiempo para detectar degradaciones de rendimiento.

---

Si tienes alguna pregunta sobre cómo usar el sistema de logs, consulta los ejemplos en `src/MercadoPago_logger_example.py` y `src/Rappi_logger_example.py`.

