# E-Ticket System Endpoints
import json
from datetime import datetime
from pathlib import Path

def setup_eticket_routes(app, simulator):
    """Setup E-Ticket API routes"""
    
    # Initialize users file if it doesn't exist
    if not Path("eticket_users.json").exists():
        with open("eticket_users.json", 'w') as f:
            json.dump({"users": []}, f)
    
    @app.post("/api/eticket/signup")
    async def eticket_signup(request: dict):
        """Register new user for E-Ticket system"""
        try:
            with open("eticket_users.json", 'r') as f:
                data = json.load(f)
            
            if any(u['email'] == request['email'] for u in data['users']):
                return {"success": False, "message": "Email already registered"}
            
            new_user = {
                "id": len(data['users']) + 1,
                "name": request['name'],
                "email": request['email'],
                "phone": request['phone'],
                "age": request['age'],
                "password": request['password'],
                "balance": 0,
                "is_senior": int(request['age']) >= 60,
                "created_at": datetime.now().isoformat()
            }
            
            data['users'].append(new_user)
            
            with open("eticket_users.json", 'w') as f:
                json.dump(data, f, indent=2)
            
            user_response = {k: v for k, v in new_user.items() if k != 'password'}
            
            return {
                "success": True,
                "message": "Account created successfully",
                "user": user_response
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    @app.post("/api/eticket/login")
    async def eticket_login(request: dict):
        """Login user"""
        try:
            with open("eticket_users.json", 'r') as f:
                data = json.load(f)
            
            user = next((u for u in data['users'] if u['email'] == request['email']), None)
            
            if not user:
                return {"success": False, "message": "User not found"}
            
            if user['password'] != request['password']:
                return {"success": False, "message": "Invalid password"}
            
            user_response = {k: v for k, v in user.items() if k != 'password'}
            
            return {
                "success": True,
                "message": "Login successful",
                "user": user_response
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    @app.get("/api/eticket/active-routes")
    async def get_active_routes_for_ticket():
        """Get only currently active routes with buses"""
        try:
            active_routes_list = []
            
            for route_id in simulator.active_routes:
                route = simulator.routes.get(route_id)
                if route:
                    bus_count = sum(1 for bus in simulator.buses.values() if bus.route_id == route_id)
                    fare = max(20, int(route.total_distance * 10))
                    
                    active_routes_list.append({
                        "route_id": route_id,
                        "name": route.name,
                        "source": route.source,
                        "destination": route.destination,
                        "fare": fare,
                        "active_buses": bus_count,
                        "distance": round(route.total_distance, 1)
                    })
            
            return {
                "success": True,
                "routes": active_routes_list,
                "total_active": len(active_routes_list)
            }
            
        except Exception as e:
            return {"success": False, "message": str(e), "routes": []}

    @app.post("/api/eticket/topup")
    async def eticket_topup(request: dict):
        """Top up user wallet"""
        try:
            with open("eticket_users.json", 'r') as f:
                data = json.load(f)
            
            user = next((u for u in data['users'] if u['email'] == request['email']), None)
            
            if not user:
                return {"success": False, "message": "User not found"}
            
            user['balance'] += int(request['amount'])
            
            with open("eticket_users.json", 'w') as f:
                json.dump(data, f, indent=2)
            
            return {
                "success": True,
                "message": "Top-up successful",
                "new_balance": user['balance']
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    @app.post("/api/eticket/purchase")
    async def eticket_purchase(request: dict):
        """Purchase E-Ticket"""
        try:
            with open("eticket_users.json", 'r') as f:
                data = json.load(f)
            
            user = next((u for u in data['users'] if u['email'] == request['email']), None)
            
            if not user:
                return {"success": False, "message": "User not found"}
            
            if request['route_id'] not in simulator.active_routes:
                return {"success": False, "message": "Route not active"}
            
            fare = 0 if user['is_senior'] else int(request['fare'])
            
            if request.get('payment_method') == 'wallet':
                if user['balance'] < fare:
                    return {"success": False, "message": "Insufficient balance"}
                
                user['balance'] -= fare
                
                with open("eticket_users.json", 'w') as f:
                    json.dump(data, f, indent=2)
            
            return {
                "success": True,
                "message": "Ticket purchased successfully",
                "ticket": {
                    "route_id": request['route_id'],
                    "fare": fare,
                    "is_free": user['is_senior'],
                    "payment_method": request.get('payment_method'),
                    "timestamp": datetime.now().isoformat()
                },
                "new_balance": user['balance']
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}
