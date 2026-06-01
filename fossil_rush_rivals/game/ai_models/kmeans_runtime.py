from dataclasses import dataclass
from typing import List


@dataclass
class KMeansModel:
    centers: List[List[float]]

    def score_zone(self, features: List[float]) -> float:
        """
        Evaluate how strategically viable a specific grid coordinate is based 
        on its proximity to our pre-computed K-Means fossil hotspots.
        
        REASONING:
        The closer we are to a known historical cluster center (hotspot), the 
        higher our likelihood of finding a fossil. We convert a physical 
        distance value into a positive score between 0.0 and 1.0.
        """
        # If no hotspots have been loaded, return default zero score
        if not self.centers:
            return 0.0
            
        best = None
        # Step 1: Compute Euclidean Distance to each of the pre-calculated hotspots
        for center in self.centers:
            # Skip if the dimension of features doesn't match the hotspot dimension
            if len(center) != len(features):
                continue
            
            # Squared distance formula (faster than calculating square roots at runtime)
            distance = 0.0
            for value, target in zip(features, center):
                diff = value - target
                distance += diff * diff
                
            # Keep track of the absolute closest hotspot center
            if best is None or distance < best:
                best = distance
                
        # If no valid distance could be calculated, return zero priority
        if best is None:
            return 0.0
            
        # Step 2: Smooth Scaling Score Formula
        # We divide 1.0 by (1.0 + best). 
        # - If distance is 0.0 (directly on hotspot): score is 1.0 / 1.0 = 1.0 (Highest Priority)
        # - As distance increases to infinity: score approaches 0.0 (Lowest Priority)
        return 1.0 / (1.0 + best)


def load_model(payload: dict) -> KMeansModel:
    centers = payload.get("centers", []) if payload else []
    return KMeansModel(centers=centers)
