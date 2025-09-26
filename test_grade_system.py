#!/usr/bin/env python3
"""
Test script to verify the updated grading system with the new score ranges.
Tests various score values to ensure correct grade assignment.
"""

def test_grade_assignment():
    """Test the grade assignment logic with various score values"""
    
    def get_grade(score):
        """Get grade based on the new score ranges"""
        if score >= 90:
            return "A+", "Exceptional Quality Recognition"
        elif score >= 80:
            return "A", "Excellent - Quality Recognition"
        elif score >= 70:
            return "B+", "Good - Quality Recognition"
        elif score >= 60:
            return "B", "Adequate - Quality Recognition"
        elif score >= 50:
            return "C", "Average - Quality Recognition"
        else:
            return "F", "Below Average - Needs Improvement"
    
    # Test cases with various scores
    test_scores = [
        (95.0, "A+", "Exceptional Quality Recognition"),
        (90.0, "A+", "Exceptional Quality Recognition"),
        (89.9, "A", "Excellent - Quality Recognition"),
        (85.0, "A", "Excellent - Quality Recognition"),
        (80.0, "A", "Excellent - Quality Recognition"),
        (79.9, "B+", "Good - Quality Recognition"),
        (75.0, "B+", "Good - Quality Recognition"),
        (70.0, "B+", "Good - Quality Recognition"),
        (69.9, "B", "Adequate - Quality Recognition"),
        (65.0, "B", "Adequate - Quality Recognition"),
        (60.0, "B", "Adequate - Quality Recognition"),
        (59.9, "C", "Average - Quality Recognition"),
        (55.0, "C", "Average - Quality Recognition"),
        (50.0, "C", "Average - Quality Recognition"),
        (49.9, "F", "Below Average - Needs Improvement"),
        (30.0, "F", "Below Average - Needs Improvement"),
        (0.0, "F", "Below Average - Needs Improvement")
    ]
    
    print("🧪 Testing Updated Grading System")
    print("=" * 60)
    print(f"{'Score':<8} {'Expected':<10} {'Actual':<10} {'Description':<35} {'Status'}")
    print("-" * 60)
    
    all_passed = True
    
    for score, expected_grade, expected_desc in test_scores:
        actual_grade, actual_desc = get_grade(score)
        
        # Check if test passed
        passed = (actual_grade == expected_grade and actual_desc == expected_desc)
        status = "✅ PASS" if passed else "❌ FAIL"
        
        if not passed:
            all_passed = False
        
        print(f"{score:<8.1f} {expected_grade:<10} {actual_grade:<10} {actual_desc:<35} {status}")
    
    print("-" * 60)
    
    if all_passed:
        print("🎉 All tests PASSED! The grading system is working correctly.")
    else:
        print("❌ Some tests FAILED! Please check the grading logic.")
    
    return all_passed

if __name__ == "__main__":
    test_grade_assignment()