from pathlib import Path
from ultralytics import YOLO


class Trainer:
    def __init__(self, model_name: str) -> None:
        self._model: YOLO = YOLO(model_name)

    def run(
        self,
        data_yaml: str,
        epochs: int,
        imgsz: int,
        batch: int,
        project_dir: str,
        run_name: str,
        device: str,
    ) -> tuple[bool, Path]:
        try:
            self._model.train(
                data=data_yaml,  # Ruta del archivo data.yaml 'datasets/dataset_20260125120000/data.yaml'
                epochs=epochs,  # Épocas
                imgsz=imgsz,  # Tamaño de imagen
                batch=batch,  # Tamaño de batch
                project=str(project_dir),  # Ruta del proyecto 'models/trained'
                name=run_name,  # Nombre del modelo entrenado 'model_20260125120000'
                device=device,  # Dispositivo de entrenamiento 0 o 'mps' o 'cpu'
                patience=50,  # Patencia para el entrenamiento
                exist_ok=True,  # Si el modelo ya existe, lo sobreescribe
                verbose=True,  # Muestra el progreso del entrenamiento
            )

            best_model_path = self._model.trainer.save_dir / "weights" / "best.pt"

            return True, best_model_path

        except Exception:
            raise
