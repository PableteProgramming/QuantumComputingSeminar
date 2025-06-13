import torch
import torch.nn as nn
import torch.optim as optim
import programs.program1
from simulation import simulate

# Dimensions
_,N = programs.program1.program1()

# Initial mean weights - parameters we want to learn
mean_weights = torch.randn(N, N, requires_grad=True)

# Fixed standard deviation for exploration
std =1.0

optimizer = optim.Adam([mean_weights], lr=0.05)

def policy_gradient_update(mean_weights, sampled_weights, reward):
    # Log probability of sampled weights under current policy (Gaussian)
    dist = torch.distributions.Normal(mean_weights, std)
    log_prob = dist.log_prob(sampled_weights).sum()

    # REINFORCE loss = -log_prob * reward (maximize reward)
    loss = -log_prob * reward
    return loss

def sample_weights_pos_float(mean, std):
    # Sample continuous weights
    sampled = mean + std * torch.randn_like(mean)
    # Clamp to zero (no negatives)
    sampled_clamped = sampled.clamp(min=0)
    # Convert to nested list of floats
    return sampled_clamped.detach().tolist()

num_episodes = 100
for episode in range(num_episodes):
    optimizer.zero_grad()

    # Sample positive float weights
    sampled_list = sample_weights_pos_float(mean_weights, std)
    print(sampled_list)

    # Get latency (environment feedback)
    latency = simulate(sampled_list)
    reward = -latency  # maximize negative latency

    # For policy gradient, use clamped continuous sample
    sampled_tensor = mean_weights + std * torch.randn_like(mean_weights)
    sampled_tensor_clamped = sampled_tensor.clamp(min=0)

    loss = policy_gradient_update(mean_weights, sampled_tensor_clamped, reward)
    loss.backward()
    optimizer.step()

    if episode % 100 == 0:
        print(f"Episode {episode} - Latency: {latency:.4f} - Reward: {reward:.4f}")

print("Training finished!")

with torch.no_grad():
    final_weights = mean_weights.clamp(min=0)
    print("Optimized mean weights matrix (positive floats):")
    print(final_weights)