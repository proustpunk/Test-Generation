import joblib
import json

class SVMWithLabels:
    def __init__(self, svm_model, category_mapping):
        self.svm_model = svm_model
        self.category_mapping = category_mapping

    def predict(self, vectors):
        # Predict using the SVM model
        predictions = self.svm_model.predict(vectors)
        # Map numerical predictions to category names
        return [self.category_mapping[str(pred)] for pred in predictions]

    @staticmethod
    def load(model_path, mapping_path):
        # Load the SVM model and the category mapping
        svm_model = joblib.load(model_path)
        with open(mapping_path, 'r') as f:
            category_mapping = json.load(f)
        return SVMWithLabels(svm_model, category_mapping)

    def save(self, model_path, mapping_path):
        # Save the SVM model and the category mapping
        joblib.dump(self.svm_model, model_path)
        with open(mapping_path, 'w') as f:
            json.dump(self.category_mapping, f)
