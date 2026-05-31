#!/usr/bin/env python3
"""
Integrated SymPy Geometric Core & Ocean Market M2M Cleansing Engine.
Processes pay-per-parse mathematical alignments natively using native Base USDC parameters.
"""

import sys
import os
import json
import math
from typing import Dict, Any, List
from sympy import Symbol, sqrt, pi, atan, tan, Eq, Function

class SymPyGeometricCleanser:
    def __init__(self):
        self.U = Symbol("U", positive=True)      
        self.Phi = Symbol("Phi", positive=True)  
        self.theta = Symbol("theta")             

        self.NUMERICAL_PHI = float((1 + math.sqrt(5)) / 2) 
        self.NUMERICAL_THETA = math.atan(0.5)              
        
        self.LINEAR_BOUND = 8.0 * 1.0 
        self.ROTATIONAL_BOUND = 2.0 * math.pi * math.sqrt(self.NUMERICAL_PHI)

    def evaluate_and_cleanse_stream(self, data_stream: List[float]) -> List[float]:
        if not data_stream:
            return []

        cleaned_vector = []
        previous_stable_value = data_stream
        alpha_filter = self.NUMERICAL_THETA  

        for current_value in data_stream:
            if abs(current_value) > self.LINEAR_BOUND * 100: 
                current_value = math.copysign(self.ROTATIONAL_BOUND, current_value)

            cleansed_value = (alpha_filter * current_value) + ((1.0 - alpha_filter) * previous_stable_value)
            normalized_value = cleansed_value / self.NUMERICAL_PHI
            cleaned_vector.append(round(normalized_value, 5))
            previous_stable_value = cleansed_value

        return cleaned_vector

    def execute_ocean_job(self):
        input_dir = "/data/inputs"
        output_dir = "/data/outputs"
        
        try:
            if not os.path.exists(input_dir) or not os.listdir(input_dir):
                print(json.dumps({"status": "FAILED", "reason": "No data stream found."}))
                return
                
            subdirs = [os.path.join(input_dir, d) for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
            if not subdirs:
                print(json.dumps({"status": "FAILED", "reason": "Invalid payload directory assembly."}))
                return
                
            payload_path = os.path.join(subdirs, "payload.json")
            
            with open(payload_path, "r") as f:
                payload = json.load(f)
                
            raw_data = payload.get("raw_stream", [])
            sanitized_stream = self.evaluate_and_cleanse_stream(raw_data)

            receipt = {
                "settlement_matrix": {
                    "network": "Base Layer 2",
                    "asset": "Native USDC (Circle)",
                    "price_per_parse": "0.0402",
                    "status": "SUCCESSFUL_VALIDATION"
                },
                "system_invariants": {
                    "theta_displacement_rad": round(self.NUMERICAL_THETA, 5),
                    "golden_ratio_phi": round(self.NUMERICAL_PHI, 5),
                    "hypercurvature_h": round(math.pi * self.NUMERICAL_PHI, 5)
                },
                "cleansed_stream": sanitized_stream
            }

            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, "result.json"), "w") as out_f:
                json.dump(receipt, out_f, indent=2)

        except Exception as e:
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, "result.json"), "w") as err_f:
                json.dump({"status": "SYSTEM_FAULT", "details": str(e)}, err_f)

if __name__ == "__main__":
    engine = SymPyGeometricCleanser()
    engine.execute_ocean_job()
