import json
from pathlib import Path
import numpy as np

def sigmoid(x):
    """
    Sigmoid Activation Function: Maps any value to a smooth probability between 0.0 and 1.0.
    np.clip prevents exponential underflow/overflow errors (numerical stability).
    """
    return 1 / (1 + np.exp(-np.clip(x, -250, 250)))

def sigmoid_deriv(x):
    """
    Derivative of Sigmoid: Used during Backpropagation to understand the slope (gradient) 
    of the activation, telling us how much to adjust the weights to correct the error.
    """
    s = sigmoid(x)
    return s * (1 - s)

def manual_mlp(X, y, hidden_sizes=(16, 8), epochs=500, lr=0.01, seed=12345):
    """
    Multi-Layer Perceptron (MLP) Backpropagation: "Veteran Intuition"
    
    PURPOSE:
    This algorithm trains a Multi-Layer Feedforward Neural Network to predict 
    the final valuation multiplier of various fossils based on historic market trends.
    
    STRATEGIC REASONING:
    Market valuation is a highly complex, non-linear problem. How a fossil's price 
    changes depends on a web of factors: its clean completeness, the market trend, 
    and the opponent's emotional state. Linear rules fail here. A Neural Network acts 
    like a "veteran's gut feeling"—parallel processing all these inputs through hidden 
    neuron layers to predict the perfect market price and outsmart the rival.
    """
    rng = np.random.default_rng(seed)
    n_samples, n_features = X.shape
    y = y.reshape(-1, 1)

    # 1. ARCHITECTURE SETUP:
    # 4 layers: Input -> Hidden 1 (16 neurons) -> Hidden 2 (8 neurons) -> Output (1 prediction value)
    layer_sizes = [n_features, hidden_sizes[0], hidden_sizes[1], 1]
    
    # Xavier/Glorot Weight Initialization:
    # We initialize weights using a normal distribution scaled by the size of the layer.
    # This prevents gradients from vanishing (shrinking to zero) or exploding (growing to infinity).
    weights = [
        rng.standard_normal((layer_sizes[i], layer_sizes[i+1])) * np.sqrt(2.0 / layer_sizes[i])
        for i in range(len(layer_sizes)-1)
    ]
    # Initialize all biases to 0.0
    biases = [np.zeros((1, layer_sizes[i+1])) for i in range(len(layer_sizes)-1)]
    
    # 2. TRAINING LOOP:
    for epoch in range(epochs):
        # --- FORWARD PASS (Forward Propagation) ---
        # Feed the inputs forward through each layer.
        # At each layer, we compute: Z = (Inputs * Weights) + Bias, and then apply Sigmoid.
        activations = [X]
        zs = []
        for i in range(len(weights)):
            z = np.dot(activations[-1], weights[i]) + biases[i]
            zs.append(z)
            # Apply Sigmoid squishing at every layer
            a = sigmoid(z)
            activations.append(a)
            
        # --- BACKWARD PASS (Backpropagation) ---
        # Calculate how wrong our final layer prediction was compared to actual historical values (y).
        # We compute the derivative of the Mean Squared Error (MSE) loss.
        delta = (activations[-1] - y) * activations[-1] * (1 - activations[-1])
        delta /= n_samples  # Average error over all samples
        
        # Propagate the error backward layer-by-layer
        for i in reversed(range(len(weights))):
            # Calculate gradient: how much the weight contributed to the final error
            dW = np.dot(activations[i].T, delta)
            db = np.sum(delta, axis=0, keepdims=True)
            
            # Backpropagate delta error to the previous layer using Chain Rule
            if i > 0:
                delta = np.dot(delta, weights[i].T) * sigmoid_deriv(zs[i-1])
                
            # --- GRADIENT DESCENT UPDATE ---
            # Adjust weights and biases in the opposite direction of the error gradient
            # Scaled by our learning rate (lr)
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

    # Manual MLP Backprop with bigger network and more training
    weights, biases = manual_mlp(features, labels, hidden_sizes=(16, 8), epochs=500, lr=0.01)

    payload = {
        "layers": [w.tolist() for w in weights],
        "biases": [b.tolist() for b in biases],
    }
    payload_path.write_text(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
