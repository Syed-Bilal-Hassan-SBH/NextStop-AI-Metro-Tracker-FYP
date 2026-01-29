#!/usr/bin/env python3
"""
Metro Bus Mobile App - Feature Integration Verification Script
Verifies that all features are correctly implemented and accessible
"""

import requests
import json
from datetime import datetime
import sys

class FeatureVerifier:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    def check_endpoint(self, method, endpoint, data=None, name=None):
        """Check if an endpoint is accessible and working"""
        url = f"{self.base_url}{endpoint}"
        name = name or f"{method} {endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, json=data or {}, timeout=5)
            
            if response.status_code in [200, 201]:
                self.results.append({
                    'name': name,
                    'status': '✅ PASS',
                    'code': response.status_code,
                    'data_size': len(response.text)
                })
                return True
            else:
                self.results.append({
                    'name': name,
                    'status': '❌ FAIL',
                    'code': response.status_code,
                    'error': response.text[:100]
                })
                return False
        except Exception as e:
            self.results.append({
                'name': name,
                'status': '❌ ERROR',
                'error': str(e)
            })
            return False
    
    def verify_all_features(self):
        """Verify all mobile app features"""
        print("=" * 80)
        print("Metro Bus Mobile App - Feature Integration Verification")
        print("=" * 80)
        print()
        
        # Route Management Features
        print("🚌 ROUTE MANAGEMENT FEATURES")
        print("-" * 80)
        self.check_endpoint("GET", "/api/routes", name="Get all routes")
        self.check_endpoint("GET", "/api/buses", name="Get all buses")
        self.check_endpoint("GET", "/api/routes/statistics", name="Get route statistics")
        self.check_endpoint("GET", "/api/routes/R1/bidirectional", name="Get bidirectional stats")
        print()
        
        # Journey Planning Features
        print("🧭 JOURNEY PLANNING FEATURES")
        print("-" * 80)
        self.check_endpoint("POST", "/api/journey/plan", 
                          data={"origin_lat": 24.8607, "origin_lng": 67.0011, 
                                "destination_lat": 24.7466, "destination_lng": 67.0199},
                          name="Plan journey")
        self.check_endpoint("GET", "/api/journey/transfer-points", name="Get transfer points")
        self.check_endpoint("GET", "/api/journey/nearby-stops?lat=24.8607&lng=67.0011&radius_km=0.5",
                          name="Find nearby stops")
        print()
        
        # Traffic & ETA Features
        print("🚦 TRAFFIC & ETA FEATURES")
        print("-" * 80)
        self.check_endpoint("GET", "/api/traffic/current", name="Get current traffic")
        self.check_endpoint("GET", "/api/eta/all", name="Get all ETA predictions")
        self.check_endpoint("GET", "/api/traffic/route/R1", name="Get route-specific traffic")
        print()
        
        # Analytics Features
        print("📈 ANALYTICS FEATURES")
        print("-" * 80)
        self.check_endpoint("GET", "/api/simulation/status", name="Get simulation status")
        self.check_endpoint("GET", "/api/routes/statistics", name="Get statistics")
        print()
        
        # Admin Features
        print("👔 ADMIN FEATURES")
        print("-" * 80)
        self.check_endpoint("GET", "/api/admin/statistics", name="Get admin statistics")
        self.check_endpoint("GET", "/api/admin/alerts", name="Get admin alerts")
        self.check_endpoint("GET", "/api/admin/performance", name="Get performance metrics")
        self.check_endpoint("POST", "/api/admin/announcement",
                          data={"title": "Test", "message": "Test", "priority": "normal"},
                          name="Send announcement")
        print()
        
        # WebSocket
        print("🔌 WEBSOCKET FEATURES")
        print("-" * 80)
        try:
            import websocket
            ws_url = self.base_url.replace("http", "ws") + "/ws/live-tracking"
            ws = websocket.create_connection(ws_url, timeout=5)
            ws.close()
            self.results.append({'name': 'WebSocket connection', 'status': '✅ PASS'})
        except Exception as e:
            self.results.append({'name': 'WebSocket connection', 'status': '❌ ERROR', 'error': str(e)})
        print()
        
        self.print_summary()
    
    def print_summary(self):
        """Print verification summary"""
        print("=" * 80)
        print("VERIFICATION RESULTS SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if '✅' in r['status'])
        failed = sum(1 for r in self.results if '❌' in r['status'])
        total = len(self.results)
        
        for result in self.results:
            status = result['status']
            name = result['name']
            print(f"{status} {name:<50}", end="")
            if 'code' in result:
                print(f" [{result['code']}]")
            elif 'error' in result:
                print(f" {result['error'][:30]}")
            else:
                print()
        
        print()
        print("=" * 80)
        print(f"TOTAL: {total} | PASSED: {passed} ✅ | FAILED: {failed} ❌")
        print(f"SUCCESS RATE: {(passed/total*100):.1f}%")
        print("=" * 80)
        print()
        
        if failed == 0:
            print("🎉 ALL FEATURES VERIFIED SUCCESSFULLY!")
            print("Mobile app is ready for production use.")
            return True
        else:
            print(f"⚠️  {failed} features need attention")
            print("Check backend logs for errors")
            return False

if __name__ == "__main__":
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    verifier = FeatureVerifier(base_url)
    success = verifier.verify_all_features()
    
    sys.exit(0 if success else 1)
