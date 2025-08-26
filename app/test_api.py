#!/usr/bin/env python3
"""
Test script for VeriGPT FastAPI service
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🧪 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Agent ready: {data['environment']['agent_ready']}")
            print(f"   OpenAI key set: {data['environment']['openai_key_set']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API service")
        return False

def test_files():
    """Test files endpoint"""
    print("\n🧪 Testing files endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/files")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Files endpoint: {data['total_files']} files found")
            return True
        else:
            print(f"❌ Files endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Files endpoint error: {e}")
        return False

def test_stats():
    """Test stats endpoint"""
    print("\n🧪 Testing stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint: {data['total_files']} files, {data['total_size_mb']} MB")
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
        return False

def test_analyze_code():
    """Test code analysis endpoint"""
    print("\n🧪 Testing code analysis endpoint...")
    try:
        test_code = """
module test_module (
    input logic clk,
    input logic rst_n,
    output logic [7:0] data
);
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            data <= 8'h00;
        end else begin
            data <= data + 1;
        end
    end
endmodule
"""
        
        payload = {
            "code": test_code,
            "model": "gpt-4",
            "temperature": 0.1
        }
        
        response = requests.post(
            f"{BASE_URL}/analyze/code",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Code analysis successful")
            print(f"   Input length: {len(data['input'])} chars")
            print(f"   Analysis length: {len(data['analysis'])} chars")
            return True
        else:
            print(f"❌ Code analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Code analysis error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting VeriGPT API tests...")
    print(f"📍 Testing against: {BASE_URL}")
    
    # Wait a bit for service to start
    print("⏳ Waiting for service to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health),
        ("Files List", test_files),
        ("Statistics", test_stats),
        ("Code Analysis", test_analyze_code)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"   ❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API service is working correctly.")
        print(f"\n📚 API Documentation:")
        print(f"   Swagger UI: {BASE_URL}/docs")
        print(f"   ReDoc: {BASE_URL}/redoc")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())
