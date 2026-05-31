import json
from pathlib import Path
import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -250, 250)))

def sigmoid_deriv(x):
    s = sigmoid(x)
    return s * (1 - s)

def manual_mlp(X, y, hidden_sizes=(8, 4), epochs=200, lr=0.05, seed=12345):
    rng = np.random.default_rng(seed)
    n_samples, n_features = X.shape
    y = y.reshape(-1, 1)

    layer_sizes = [n_features, hidden_sizes[0], hidden_sizes[1], 1]
    weights = [rng.standard_normal((layer_sizes[i], layer_sizes[i+1])) * 0.1 for i in range(len(layer_sizes)-1)]
    biases = [np.zeros((1, layer_sizes[i+1])) for i in range(len(layer_sizes)-1)]
    
    for _ in range(epochs):
        # Forward
        activations = [X]
        zs = []
        for i in range(len(weights)):
            z = np.dot(activations[-1], weights[i]) + biases[i]
            zs.append(z)
            a = sigmoid(z) if i < len(weights) - 1 else z # Linear output layer
            activations.append(a)
            
        # Backward
        delta = (activations[-1] - y) / n_samples
        
        for i in reversed(range(len(weights))):
            dW = np.dot(activations[i].T, delta)
            db = np.sum(delta, axis=0, keepdims=True)
            
            if i > 0:
                delta = np.dot(delta, weights[i].T) * sigmoid_deriv(zs[i-1])
                
            weights[i] -= lr * dW
            biases[i] -= lr * db
            
    return weights, biases

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    payload_path = data_dir / "market_model.json"

    data = np.load(data_dir / "synthetic_data.npz")
    features = data["features"]
    labels = data.get("values", data["labels"]).astype(float)

    # Manual MLP Backprop
    weights, biases = manual_mlp(features, labels)

    payload = {
        "layers": [w.tolist() for w in weights],
        "biases": [b.tolist() for b in biases],
    }
    payload_path.write_text(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
