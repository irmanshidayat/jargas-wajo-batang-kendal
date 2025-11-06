"""
Script manual testing untuk menguji quantity preservation
Jalankan: python -m app.tests.test_quantity_manual
atau dari root: python backend/app/tests/test_quantity_manual.py
"""

import json
import sys
import os

# Add backend to path jika diperlukan
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)

def test_frontend_to_backend_flow():
    """Simulasi alur data dari frontend ke backend"""
    print("=" * 60)
    print("TEST: Frontend to Backend Quantity Flow")
    print("=" * 60)
    
    # Step 1: Frontend - Input dari form
    print("\n[STEP 1] Frontend - Input dari form:")
    form_items = [
        {"material_id": "1", "quantity": "20"},
        {"material_id": "2", "quantity": "10"},
    ]
    print(f"  Form Input: {form_items}")
    
    # Step 2: Frontend - Convert dengan parseInt
    print("\n[STEP 2] Frontend - Convert dengan parseInt:")
    converted_items = []
    for item in form_items:
        converted = {
            "material_id": int(item["material_id"]),
            "quantity": int(item["quantity"])
        }
        converted_items.append(converted)
        print(f"  '{item['quantity']}' -> {converted['quantity']} (type: {type(converted['quantity'])})")
    
    # Verify
    assert converted_items[0]["quantity"] == 20, "Quantity 20 should remain 20"
    assert converted_items[1]["quantity"] == 10, "Quantity 10 should remain 10"
    print("  ✓ Conversion PASSED")
    
    # Step 3: Frontend - JSON.stringify
    print("\n[STEP 3] Frontend - JSON.stringify:")
    items_json = json.dumps(converted_items)
    print(f"  JSON String: {items_json}")
    
    # Step 4: Backend - json.loads
    print("\n[STEP 4] Backend - json.loads:")
    parsed_items = json.loads(items_json)
    print(f"  Parsed Items: {parsed_items}")
    for i, item in enumerate(parsed_items):
        print(f"  Item {i+1}: quantity={item['quantity']} (type: {type(item['quantity'])})")
    
    # Verify
    assert parsed_items[0]["quantity"] == 20, "Quantity 20 should remain 20 after JSON"
    assert parsed_items[1]["quantity"] == 10, "Quantity 10 should remain 10 after JSON"
    assert isinstance(parsed_items[0]["quantity"], int), "Should be int type"
    print("  ✓ JSON Parse PASSED")
    
    # Step 5: Backend - int() conversion
    print("\n[STEP 5] Backend - int() conversion:")
    normalized_items = []
    for idx, item in enumerate(parsed_items):
        raw_qty = item.get("quantity")
        qty_int = int(item.get("quantity"))
        normalized_items.append({
            "material_id": int(item.get("material_id")),
            "quantity": qty_int
        })
        print(f"  Item {idx+1}: {raw_qty} (type: {type(raw_qty)}) -> {qty_int} (type: {type(qty_int)})")
    
    # Verify
    assert normalized_items[0]["quantity"] == 20, "Quantity 20 should remain 20 after int()"
    assert normalized_items[1]["quantity"] == 10, "Quantity 10 should remain 10 after int()"
    print("  ✓ int() Conversion PASSED")
    
    # Final Verification
    print("\n" + "=" * 60)
    print("FINAL VERIFICATION:")
    print("=" * 60)
    print(f"  Original Quantity 1: {form_items[0]['quantity']}")
    print(f"  Final Quantity 1:    {normalized_items[0]['quantity']}")
    print(f"  Match: {int(form_items[0]['quantity']) == normalized_items[0]['quantity']}")
    
    print(f"\n  Original Quantity 2: {form_items[1]['quantity']}")
    print(f"  Final Quantity 2:    {normalized_items[1]['quantity']}")
    print(f"  Match: {int(form_items[1]['quantity']) == normalized_items[1]['quantity']}")
    
    if (int(form_items[0]['quantity']) == normalized_items[0]['quantity'] and
        int(form_items[1]['quantity']) == normalized_items[1]['quantity']):
        print("\n✅ ALL TESTS PASSED - Quantity preserved correctly!")
        return True
    else:
        print("\n❌ TEST FAILED - Quantity changed!")
        return False


def test_edge_cases():
    """Test edge cases untuk quantity"""
    print("\n" + "=" * 60)
    print("TEST: Edge Cases")
    print("=" * 60)
    
    edge_cases = [
        ("1", 1),
        ("10", 10),
        ("20", 20),
        ("99", 99),
        ("100", 100),
        ("999", 999),
        ("9999", 9999),
    ]
    
    all_passed = True
    for input_str, expected in edge_cases:
        # Simulasi flow
        parsed = int(input_str)
        json_str = json.dumps([{"quantity": parsed}])
        loaded = json.loads(json_str)
        final = int(loaded[0]["quantity"])
        
        passed = final == expected
        status = "✓" if passed else "✗"
        print(f"  {status} '{input_str}' -> {final} (expected: {expected})")
        
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ All edge cases PASSED!")
    else:
        print("\n❌ Some edge cases FAILED!")
    
    return all_passed


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("QUANTITY PRESERVATION MANUAL TESTING")
    print("=" * 60)
    
    test1_passed = test_frontend_to_backend_flow()
    test2_passed = test_edge_cases()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1)

