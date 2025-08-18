import kfp
from kfp import dsl

# Define un componente de Python para escribir un archivo.
# Usa `Output[dsl.Artifact]` para el parámetro de salida.
@dsl.component
def write_test_file(message: str, output_file: dsl.Output[dsl.Artifact]):
    # El archivo se escribe en `output_file.path`.
    with open(output_file.path, 'w') as f:
        f.write(message)
    print(f"Test file written to: {output_file.path}")

# Define un componente para leer el archivo.
# Usa `Input[dsl.Artifact]` para el parámetro de entrada.
@dsl.component(
    base_image='python:3.9',
    packages_to_install=["pandas", "fsspec", "minio"]
)
def read_test_file(input_file: dsl.Input[dsl.Artifact]):
    """
    Lee un archivo desde la ruta de entrada del artefacto y muestra su contenido.
    """
    from minio import Minio
    from minio.error import S3Error
    from io import BytesIO
    import pandas as pd

    def read_minio_file(bucket_name, object_name):
        """
        Lee un archivo de un bucket de MinIO.
    
        Args:
            bucket_name (str): El nombre del bucket.
            object_name (str): El nombre del objeto (archivo) a leer.
        """
        try:
            # 1. Configurar el cliente MinIO
            client = Minio(
                "minio-service.kubeflow.svc.cluster.local:9000",  # Por ejemplo: "play.min.io"
                access_key="minio",  # Reemplaza con tu access key
                secret_key="minio123",  # Reemplaza con tu secret key
                secure=False  # Usa True para HTTPS, False para HTTP
            )
    
            # 2. Obtener el objeto del bucket
            response = client.get_object(bucket_name, object_name)
            
            # 3. Leer el contenido del objeto
            csv_data = BytesIO(response.read())
            
            return pd.read_csv(csv_data)
    
        except S3Error as err:
            print(f"Error al leer el archivo desde MinIO: {err}")
        finally:
            # Cerrar el stream de respuesta para liberar recursos
            if 'response' in locals() and response:
                response.close()
                response.release_conn()    
    

    # Ejemplo de uso
    mi_bucket = "object-creation-project"  # Reemplaza con el nombre de tu bucket
    mi_archivo = "dataset/test.csv"     # Reemplaza con el nombre de tu archivo
    df = read_minio_file(mi_bucket, mi_archivo)
    print(df)
    
    # El archivo se lee desde `input_file.path`.
    with open(input_file.path, 'r') as f:
        content = f.read()
    print(f"File content: {content}")


# Define el pipeline.
@dsl.pipeline(
    name='Test Pipeline Root',
    description='Tests the pipeline_root configuration'
)
def test_pipeline_root(message: str = 'Hello World!'):
    # Paso 1: Escribir el archivo.
    # El resultado es un objeto de tipo `dsl.Artifact`.
    write_task = write_test_file(message=message)

    # Paso 2: Verificar la lectura del archivo.
    # Pasa el objeto `dsl.Artifact` de la primera tarea como entrada a la segunda.
    read_task = read_test_file(
        input_file=write_task.outputs['output_file']
    )

# Compila el pipeline para su ejecución.
if __name__ == '__main__':
    kfp.compiler.Compiler().compile(test_pipeline_root, 'test_pipeline_root.yaml')