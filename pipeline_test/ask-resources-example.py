import kfp
import kfp.dsl as dsl
from typing import NamedTuple

# 1. Define tu componente de Python
@dsl.component
def preprocess_data() -> NamedTuple('Outputs', [('data', str)]):
    """
    Componente que simula la preparación de datos.
    """
    import time
    print("Preprocesando datos...")
    time.sleep(5)
    return ('Datos procesados',)

# 2. Define otro componente para una tarea pesada
@dsl.component
def train_model(data: str) -> str:
    """
    Componente que simula el entrenamiento de un modelo.
    """
    print(f"Iniciando entrenamiento con {data}...")
    return "Modelo entrenado"

# 3. Define el pipeline
@dsl.pipeline(
    name='Heavy-Resource-Pipeline',
    description='Pipeline que demuestra la configuración de recursos.'
)
def heavy_resource_pipeline():
    # Paso 1: Preprocesar datos
    preprocess_task = preprocess_data()
    
    # Paso 2: Entrenar el modelo (aquí es donde se aplican los recursos)
    train_task = train_model(data=preprocess_task.outputs['data'])

    # --- Configuración de recursos (CORRECTA) ---
    # Aplica los métodos de recursos directamente a la tarea 'train_task'.
    
    # Establece los requests y limits de CPU y memoria
    train_task.set_cpu_limit('4')     # Límite de CPU
    train_task.set_memory_limit('8Gi')  # Límite de memoria
    train_task.set_cpu_request('2')    # Solicitud de CPU
    train_task.set_memory_request('4Gi') # Solicitud de memoria

# 4. Compila y ejecuta el pipeline (en tu entorno de Kubeflow)
kfp.compiler.Compiler().compile(
    pipeline_func=heavy_resource_pipeline,
    package_path='pipeline_with_resources.yaml'
)