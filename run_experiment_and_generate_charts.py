#!/usr/bin/env python3
"""
COMP2611 Part B - Automated Experiment Runner with Chart Generation
This script runs the search experiments and automatically generates charts.
"""

import subprocess
import sys
import os
import csv
import matplotlib.pyplot as plt
import numpy as np

def run_experiments(seeds=5, max_nodes=10000):
    """Run the search experiments and save results to CSV files."""
    print("=" * 60)
    print("Running COMP2611 Part B Experiments")
    print("=" * 60)
    
    # Change to code directory
    os.chdir('code')
    
    # Run experiment to generate summary.csv
    print(f"\n1. Running experiments with {seeds} seeds...")
    cmd = [
        'python3', 'main.py', 'experiment',
        '--seeds', str(seeds),
        '--max-nodes', str(max_nodes),
        '--csv', '../summary.csv'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✓ Experiments completed successfully")
        
        # Print the summary table
        print("\n" + "=" * 60)
        print("Experiment Results Summary")
        print("=" * 60)
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running experiments: {e}")
        print(f"Stderr: {e.stderr}")
        return False
    
    # Run again to get detailed results
    print(f"\n2. Generating detailed results...")
    cmd = [
        'python3', 'main.py', 'experiment',
        '--seeds', str(seeds),
        '--max-nodes', str(max_nodes),
        '--csv', '../results.csv'
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✓ Detailed results saved to results.csv")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error generating detailed results: {e}")
    
    # Return to original directory
    os.chdir('..')
    return True

def generate_charts():
    """Generate charts from the experiment results."""
    print("\n" + "=" * 60)
    print("Generating Charts")
    print("=" * 60)
    
    # Read the summary data
    try:
        with open('summary.csv', 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except FileNotFoundError:
        print("✗ Error: summary.csv not found. Please run experiments first.")
        return False
    
    # Prepare data structures
    cases = ['easy', 'medium', 'hard']
    algorithms = ['bfs', 'dfs_fixed', 'dfs_random', 'best_first', 'astar']
    algorithm_names = ['BFS', 'DFS-Fixed', 'DFS-Rand', 'BestFirst', 'A*']
    heuristics = ['waypoints', 'next', 'goal', 'zero']
    
    # Helper function to get data values
    def get_value(case, algorithm, heuristic=None, field='nodes_mean'):
        for row in data:
            if (row['case'] == case and 
                row['algorithm'] == algorithm and 
                (heuristic is None or row['heuristic'] == heuristic)):
                try:
                    return float(row[field])
                except (ValueError, KeyError):
                    return 0.0
        return 0.0
    
    # Set up matplotlib style
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Figure 1: Nodes Expanded Comparison
    print("1. Creating nodes comparison chart...")
    fig1, axes1 = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
    
    for idx, case in enumerate(cases):
        ax = axes1[idx]
        
        # Get values for each algorithm
        values = []
        labels = []
        
        for algo in algorithms:
            if algo in ['astar', 'best_first']:
                # Use waypoints heuristic for informed algorithms
                val = get_value(case, algo, 'waypoints', 'nodes_mean')
            else:
                val = get_value(case, algo, None, 'nodes_mean')
            
            if val > 0:
                values.append(val)
                labels.append(algorithm_names[algorithms.index(algo)])
        
        bars = ax.bar(labels, values, color=plt.cm.Set3(np.arange(len(values))/len(values)))
        ax.set_title(f'Case: {case.capitalize()}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Algorithm', fontsize=10)
        if idx == 0:
            ax.set_ylabel('Nodes Expanded', fontsize=10)
        ax.tick_params(axis='x', rotation=45, labelsize=9)
        ax.tick_params(axis='y', labelsize=9)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    fig1.suptitle('Nodes Expanded by Algorithm and Test Case', fontsize=14, fontweight='bold')
    fig1.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig1.savefig('nodes_comparison.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved as nodes_comparison.png")
    
    # Figure 2: Path Cost Comparison
    print("2. Creating path cost comparison chart...")
    fig2, axes2 = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
    
    for idx, case in enumerate(cases):
        ax = axes2[idx]
        
        values = []
        labels = []
        
        for algo in algorithms:
            if algo in ['astar', 'best_first']:
                val = get_value(case, algo, 'waypoints', 'path_cost_mean')
            else:
                val = get_value(case, algo, None, 'path_cost_mean')
            
            if val > 0:
                values.append(val)
                labels.append(algorithm_names[algorithms.index(algo)])
        
        bars = ax.bar(labels, values, color=plt.cm.Set3(np.arange(len(values))/len(values)))
        ax.set_title(f'Case: {case.capitalize()}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Algorithm', fontsize=10)
        if idx == 0:
            ax.set_ylabel('Path Cost', fontsize=10)
        ax.tick_params(axis='x', rotation=45, labelsize=9)
        ax.tick_params(axis='y', labelsize=9)
        ax.grid(axis='y', alpha=0.3)
        
        # Add optimal cost line
        optimal_cost = get_value(case, 'bfs', None, 'path_cost_mean')
        ax.axhline(y=optimal_cost, color='red', linestyle='--', alpha=0.7, 
                  linewidth=2, label='Optimal Cost (BFS)')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        if idx == 2:
            ax.legend(fontsize=9)
    
    fig2.suptitle('Path Cost Comparison (Red line = Optimal BFS Cost)', fontsize=14, fontweight='bold')
    fig2.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig2.savefig('path_cost_comparison.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved as path_cost_comparison.png")
    
    # Figure 3: Heuristic Effectiveness for A*
    print("3. Creating heuristic effectiveness chart...")
    fig3, ax3 = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(cases))
    width = 0.2
    colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B2']
    
    for i, heuristic in enumerate(heuristics):
        nodes = []
        for case in cases:
            val = get_value(case, 'astar', heuristic, 'nodes_mean')
            nodes.append(val)
        
        ax3.bar(x + (i - 1.5) * width, nodes, width, 
                label=heuristic.capitalize(), color=colors[i])
    
    ax3.set_xlabel('Test Case', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Nodes Expanded', fontsize=11, fontweight='bold')
    ax3.set_title('A* Search: Heuristic Effectiveness Comparison', fontsize=13, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels([case.capitalize() for case in cases], fontsize=11)
    ax3.legend(fontsize=10)
    ax3.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, heuristic in enumerate(heuristics):
        for j, case in enumerate(cases):
            val = get_value(case, 'astar', heuristic, 'nodes_mean')
            ax3.text(x[j] + (i - 1.5) * width, val + 1, 
                    f'{int(val)}', ha='center', va='bottom', fontsize=9)
    
    fig3.tight_layout()
    fig3.savefig('heuristic_effectiveness.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved as heuristic_effectiveness.png")
    
    # Figure 4: Algorithm Efficiency Scatter Plot
    print("4. Creating algorithm efficiency scatter plot...")
    fig4, ax4 = plt.subplots(figsize=(10, 8))
    
    # Prepare scatter data
    scatter_data = []
    markers = ['o', 's', '^', 'D', 'v']
    colors_scatter = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for algo_idx, algo in enumerate(algorithms):
        algo_name = algorithm_names[algorithms.index(algo)]
        
        for case in cases:
            if algo in ['astar', 'best_first']:
                nodes = get_value(case, algo, 'waypoints', 'nodes_mean')
                cost = get_value(case, algo, 'waypoints', 'path_cost_mean')
            else:
                nodes = get_value(case, algo, None, 'nodes_mean')
                cost = get_value(case, algo, None, 'path_cost_mean')
            
            if nodes > 0 and cost > 0:
                optimal_cost = get_value(case, 'bfs', None, 'path_cost_mean')
                cost_ratio = optimal_cost / cost if cost > 0 else 0
                
                ax4.scatter(nodes, cost_ratio, 
                          marker=markers[algo_idx % len(markers)],
                          s=150, color=colors_scatter[algo_idx],
                          alpha=0.7, label=algo_name if case == cases[0] else "")
                
                # Add case label
                ax4.annotate(case[0].upper(), (nodes, cost_ratio),
                           textcoords="offset points", xytext=(0,10),
                           ha='center', fontsize=8, fontweight='bold')
    
    ax4.axhline(y=1.0, color='red', linestyle='--', alpha=0.7, 
               linewidth=2, label='Optimal (Ratio=1.0)')
    ax4.set_xlabel('Nodes Expanded', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Optimality Ratio (Optimal/Actual)', fontsize=11, fontweight='bold')
    ax4.set_title('Algorithm Efficiency: Search Effort vs Solution Quality', 
                 fontsize=13, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(alpha=0.3)
    
    fig4.tight_layout()
    fig4.savefig('algorithm_efficiency.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved as algorithm_efficiency.png")
    
    # Generate summary statistics
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)
    print("| Algorithm  | Avg Nodes | Avg Path Cost | Optimality |")
    print("|------------|-----------|---------------|------------|")
    
    for algo in algorithms:
        algo_name = algorithm_names[algorithms.index(algo)]
        
        total_nodes = 0
        total_cost = 0
        count = 0
        
        for case in cases:
            if algo in ['astar', 'best_first']:
                nodes = get_value(case, algo, 'waypoints', 'nodes_mean')
                cost = get_value(case, algo, 'waypoints', 'path_cost_mean')
            else:
                nodes = get_value(case, algo, None, 'nodes_mean')
                cost = get_value(case, algo, None, 'path_cost_mean')
            
            if nodes > 0:
                total_nodes += nodes
                total_cost += cost
                count += 1
        
        if count > 0:
            avg_nodes = total_nodes / count
            avg_cost = total_cost / count
            
            # Calculate optimality
            optimality_sum = 0
            optimal_count = 0
            for case in cases:
                optimal_cost = get_value(case, 'bfs', None, 'path_cost_mean')
                if algo in ['astar', 'best_first']:
                    algo_cost = get_value(case, algo, 'waypoints', 'path_cost_mean')
                else:
                    algo_cost = get_value(case, algo, None, 'path_cost_mean')
                
                if optimal_cost > 0 and algo_cost > 0:
                    optimality = optimal_cost / algo_cost
                    optimality_sum += optimality
                    optimal_count += 1
            
            avg_optimality = optimality_sum / optimal_count if optimal_count > 0 else 0
            
            print(f"| {algo_name:10} | {avg_nodes:9.1f} | {avg_cost:13.1f} | {avg_optimality:10.2f} |")
    
    print("\n" + "=" * 60)
    print("Chart Generation Complete!")
    print("=" * 60)
    print("Generated charts:")
    print("  • nodes_comparison.png - Nodes expanded comparison")
    print("  • path_cost_comparison.png - Path cost comparison")
    print("  • heuristic_effectiveness.png - Heuristic effectiveness")
    print("  • algorithm_efficiency.png - Algorithm efficiency scatter plot")
    print("\nData files:")
    print("  • summary.csv - Summary statistics")
    print("  • results.csv - Detailed results")
    
    return True

def main():
    """Main function to run experiments and generate charts."""
    print("COMP2611 Part B - Automated Experiment Runner")
    print("=" * 60)
    
    # Get parameters from command line or use defaults
    seeds = 5
    max_nodes = 10000
    
    if len(sys.argv) > 1:
        try:
            seeds = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid seed count '{sys.argv[1]}', using default {seeds}")
    
    if len(sys.argv) > 2:
        try:
            max_nodes = int(sys.argv[2])
        except ValueError:
            print(f"Warning: Invalid max nodes '{sys.argv[2]}', using default {max_nodes}")
    
    print(f"Parameters: seeds={seeds}, max_nodes={max_nodes}")
    
    # Run experiments
    if not run_experiments(seeds, max_nodes):
        print("\n✗ Experiment failed. Exiting.")
        return 1
    
    # Generate charts
    if not generate_charts():
        print("\n✗ Chart generation failed.")
        return 1
    
    print("\n" + "=" * 60)
    print("SUCCESS: Experiments and chart generation completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the generated charts in the current directory")
    print("2. Check the CSV files for detailed results")
    print("3. Update your report with the new data and charts")
    print("\nTo run again with different parameters:")
    print("  python3 run_experiment_and_generate_charts.py [seeds] [max_nodes]")
    print("  Example: python3 run_experiment_and_generate_charts.py 10 5000")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())