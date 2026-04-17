import React, {useEffect, useState, useRef} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Dimensions,
  ScrollView,
  Modal,
  Alert,
  TextInput,
  FlatList,
} from 'react-native';
import WebView from 'react-native-webview';
import LoginScreen from './LoginScreen';
import SignupScreen from './SignupScreen';
import {API_CONFIG} from '../config/api';

const {height: SCREEN_HEIGHT} = Dimensions.get('window');
const API_URL = API_CONFIG.BASE_URL;

interface Bus {
  bus_id: string;
  current_lat: number;
  current_lng: number;
  status: string;
  route_id: string;
  speed?: number;
}

interface User {
  name: string;
  email: string;
  age: number;
  balance: number;
  is_senior: boolean;
}

interface Stop {
  id: string;
  name: string;
  location: [number, number];
  connected_routes: string[];
}

type JourneyPreference = 'time' | 'money' | 'hybrid';
type JourneyMode = 'stops' | 'map';

interface JourneyLeg {
  route_id: string;
  route_name: string;
  direction: string;
  board_stop: string;
  board_location: [number, number];
  alight_stop: string;
  alight_location: [number, number];
  distance_km: number;
  travel_min: number;
  fare_rs: number;
}

interface JourneyOption {
  journey_id: string;
  route_names: string[];
  summary: {
    transfers_required: number;
    total_distance_km: number;
    total_fare_rs: number;
    estimated_total_time_minutes: number;
    score: number;
  };
  nearest_stops?: {
    origin?: {stop_name?: string; walking_distance_km?: number; walking_time_minutes?: number};
    destination?: {stop_name?: string; walking_distance_km?: number; walking_time_minutes?: number};
  };
  segments: JourneyLeg[];
  instructions: {step: number; type: string; instruction: string}[];
}

const TOPUP_AMOUNTS = [100, 200, 500, 1000];
const PAYMENT_METHODS = ['EasyPaisa', 'JazzCash', 'NayaPay', 'SadaPay'];
const TICKET_FARE_PER_KM = 3;

interface TicketReceipt {
  ticket_id: string;
  from_stop: string;
  to_stop: string;
  distance_km: number;
  fare_rs: number;
  issued_at: string;
  qr_code: string;
}

const MapScreen = () => {
  const [buses, setBuses] = useState<Bus[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState('');
  const [activeModal, setActiveModal] = useState<'list' | 'eticket' | 'journey' | null>(null);
  const [authScreen, setAuthScreen] = useState<'login' | 'signup' | null>(null);
  const [user, setUser] = useState<User | null>(null);

  // Top-up state
  const [showTopup, setShowTopup] = useState(false);
  const [selectedAmount, setSelectedAmount] = useState<number | null>(null);
  const [customAmount, setCustomAmount] = useState('');
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null);
  const [topupLoading, setTopupLoading] = useState(false);
  const [ticketFromStop, setTicketFromStop] = useState<Stop | null>(null);
  const [ticketToStop, setTicketToStop] = useState<Stop | null>(null);
  const [ticketSelectingStop, setTicketSelectingStop] = useState<'from' | 'to' | null>(null);
  const [ticketFromSearch, setTicketFromSearch] = useState('');
  const [ticketToSearch, setTicketToSearch] = useState('');
  const [ticketLoading, setTicketLoading] = useState(false);
  const [ticketReceipt, setTicketReceipt] = useState<TicketReceipt | null>(null);

  // Journey planner state
  const [stops, setStops] = useState<Stop[]>([]);
  const [stopsLoading, setStopsLoading] = useState(false);
  const [fromStop, setFromStop] = useState<Stop | null>(null);
  const [toStop, setToStop] = useState<Stop | null>(null);
  const [fromSearch, setFromSearch] = useState('');
  const [toSearch, setToSearch] = useState('');
  const [selectingStop, setSelectingStop] = useState<'from' | 'to' | null>(null);
  const [journeyLoading, setJourneyLoading] = useState(false);
  const [journeyResults, setJourneyResults] = useState<JourneyOption[] | null>(null);
  const [journeyError, setJourneyError] = useState('');
  const [journeyMode, setJourneyMode] = useState<JourneyMode>('stops');
  const [maxTransfers, setMaxTransfers] = useState<number>(2);
  const [preference, setPreference] = useState<JourneyPreference>('hybrid');
  const [expandedJourneyId, setExpandedJourneyId] = useState<string | null>(null);
  const [fromPoint, setFromPoint] = useState<[number, number] | null>(null);
  const [toPoint, setToPoint] = useState<[number, number] | null>(null);
  const [selectingPoint, setSelectingPoint] = useState<'from' | 'to' | null>(null);
  const [showLayerPopup, setShowLayerPopup] = useState(false);
  const [showFleetLayer, setShowFleetLayer] = useState(true);
  const [showRoutesLayer, setShowRoutesLayer] = useState(true);
  const [showStationsLayer, setShowStationsLayer] = useState(true);
  const [showTrafficLayer, setShowTrafficLayer] = useState(false);
  const [selectedJourney, setSelectedJourney] = useState<JourneyOption | null>(null);
  const [showJourneySteps, setShowJourneySteps] = useState(false);

  const webviewRef = useRef<any>(null);

  const fetchBuses = async () => {
    try {
      const r = await fetch(`${API_URL}/api/buses`);
      const data = await r.json();
      const arr = Array.isArray(data) ? data : data.buses || [];
      setBuses(arr);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (e) {
      console.error('❌ Fetch error:', e);
    } finally {
      setLoading(false);
    }
  };

  const fetchStops = async () => {
    setStopsLoading(true);
    try {
      const r = await fetch(`${API_URL}${API_CONFIG.ENDPOINTS.SIMULATION_STATUS}`);
      const data = await r.json();
      const routes = data?.routes ? Object.values(data.routes) : [];

      const collected: Stop[] = [];
      const byKey = new Map<string, Stop>();

      routes.forEach((route: any) => {
        if (!route?.stops || !Array.isArray(route.stops)) return;
        route.stops.forEach((stop: any) => {
          const lat = stop.latitude;
          const lng = stop.longitude;
          const name = stop.name;
          if (typeof lat !== 'number' || typeof lng !== 'number' || !name) return;
          const key = `${lat.toFixed(5)},${lng.toFixed(5)}`;
          const existing = byKey.get(key);
          if (existing) {
            if (!existing.connected_routes.includes(route.route_id)) {
              existing.connected_routes.push(route.route_id);
            }
          } else {
            const s: Stop = {
              id: key,
              name,
              location: [lat, lng],
              connected_routes: [route.route_id],
            };
            byKey.set(key, s);
            collected.push(s);
          }
        });
      });

      collected.sort((a, b) => a.name.localeCompare(b.name));
      setStops(collected);
    } catch (e) {
      console.error('Failed to fetch stops:', e);
    } finally {
      setStopsLoading(false);
    }
  };

  const fetchActiveTicketStops = async () => {
    setStopsLoading(true);
    try {
      const statusRes = await fetch(`${API_URL}${API_CONFIG.ENDPOINTS.SIMULATION_STATUS}`);
      const statusData = await statusRes.json();
      const routes = statusData?.routes ? Object.values(statusData.routes) : [];

      // Active route IDs based on currently active buses in mobile state.
      const activeRouteIds = new Set(
        buses
          .map(b => b.route_id)
          .filter(Boolean)
      );
      const activeFromStatus = Array.isArray(statusData?.active_routes) ? statusData.active_routes : [];
      activeFromStatus.forEach((rid: string) => activeRouteIds.add(rid));

      const collected: Stop[] = [];
      const byKey = new Map<string, Stop>();

      routes.forEach((route: any) => {
        if (!route?.route_id || !activeRouteIds.has(route.route_id)) return;
        if (!route?.stops || !Array.isArray(route.stops)) return;

        route.stops.forEach((stop: any) => {
          const lat = stop.latitude;
          const lng = stop.longitude;
          const name = stop.name;
          if (typeof lat !== 'number' || typeof lng !== 'number' || !name) return;

          const key = `${lat.toFixed(5)},${lng.toFixed(5)}`;
          const existing = byKey.get(key);
          if (existing) {
            if (!existing.connected_routes.includes(route.route_id)) {
              existing.connected_routes.push(route.route_id);
            }
          } else {
            const s: Stop = {
              id: key,
              name,
              location: [lat, lng],
              connected_routes: [route.route_id],
            };
            byKey.set(key, s);
            collected.push(s);
          }
        });
      });

      collected.sort((a, b) => a.name.localeCompare(b.name));
      setStops(collected);
    } catch (e) {
      console.error('Failed to fetch active ticket stops:', e);
    } finally {
      setStopsLoading(false);
    }
  };

  useEffect(() => {
    fetchBuses();
    const iv = setInterval(fetchBuses, 5000);
    return () => clearInterval(iv);
  }, []);

  const openModal = (type: 'list' | 'eticket' | 'journey') => {
    setShowTopup(false);
    setJourneyResults(null);
    setJourneyError('');
    setSelectingStop(null);
    setExpandedJourneyId(null);
    setSelectingPoint(null);
    setActiveModal(type);
    if (type === 'journey' && stops.length === 0) {
      fetchStops();
    }
    if (type === 'eticket') {
      setTicketReceipt(null);
      setTicketFromStop(null);
      setTicketToStop(null);
      fetchActiveTicketStops();
    }
  };

  const closeModal = () => {
    setShowTopup(false);
    setSelectingStop(null);
    setTicketSelectingStop(null);
    setActiveModal(null);
  };

  const handleLoginSuccess = (userData: User) => {
    setUser(userData);
    setAuthScreen(null);
  };

  const handleSignupSuccess = (userData: User) => {
    setUser(userData);
    setAuthScreen(null);
  };

  const handleLogout = () => {
    setUser(null);
    setShowTopup(false);
  };

  const handleTopup = async () => {
    const finalAmount = customAmount ? parseInt(customAmount) : selectedAmount;
    if (!finalAmount || finalAmount <= 0) {
      Alert.alert('Error', 'Please select or enter a valid amount');
      return;
    }
    if (!selectedMethod) {
      Alert.alert('Error', 'Please select a payment method');
      return;
    }
    setTopupLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/eticket/topup`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email: user?.email, amount: finalAmount, method: selectedMethod}),
      });
      const data = await res.json();
      if (data.success) {
        setUser(prev => prev ? {...prev, balance: data.new_balance} : prev);
        setShowTopup(false);
        setSelectedAmount(null);
        setCustomAmount('');
        setSelectedMethod(null);
        Alert.alert('✅ Success', `Rs. ${finalAmount} added via ${selectedMethod}!`);
      } else {
        Alert.alert('Failed', data.message || 'Top-up failed');
      }
    } catch (e) {
      Alert.alert('Error', 'Could not connect to server');
    } finally {
      setTopupLoading(false);
    }
  };

  const handlePlanJourney = async () => {
    if (journeyMode === 'stops') {
      if (!fromStop || !toStop) {
        Alert.alert('Error', 'Please select both Origin and Destination stops');
        return;
      }
      if (fromStop.id === toStop.id) {
        Alert.alert('Error', 'Origin and Destination cannot be the same stop');
        return;
      }
    } else {
      if (!fromPoint || !toPoint) {
        Alert.alert('Error', 'Please set both Origin and Destination points on the map');
        return;
      }
    }
    setJourneyLoading(true);
    setJourneyResults(null);
    setJourneyError('');
    try {
      const payload: any = {
        max_transfers: maxTransfers,
        preference: preference,
      };

      if (journeyMode === 'stops') {
        payload.origin_stop = fromStop?.name;
        payload.destination_stop = toStop?.name;
      } else {
        payload.origin_lat = fromPoint?.[0];
        payload.origin_lng = fromPoint?.[1];
        payload.destination_lat = toPoint?.[0];
        payload.destination_lng = toPoint?.[1];
      }

      const res = await fetch(`${API_URL}${API_CONFIG.ENDPOINTS.JOURNEY_PLAN}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data?.success === false) {
        setJourneyError(data?.message || 'No routes found');
        return;
      }
      if (data?.detail) {
        setJourneyError(data.detail);
        return;
      }
      if (Array.isArray(data?.journeys) && data.journeys.length > 0) {
        setJourneyResults(data.journeys);
        setExpandedJourneyId(data.journeys[0].journey_id);
      } else {
        setJourneyError('No routes found');
      }
    } catch (e) {
      setJourneyError('Could not connect to server');
    } finally {
      setJourneyLoading(false);
    }
  };

  const filteredStops = (search: string) => {
    if (!search.trim()) return stops;
    return stops.filter(s =>
      s.name.toLowerCase().includes(search.toLowerCase())
    );
  };

  const haversineKm = (a: [number, number], b: [number, number]) => {
    const toRad = (v: number) => (v * Math.PI) / 180;
    const R = 6371;
    const dLat = toRad(b[0] - a[0]);
    const dLon = toRad(b[1] - a[1]);
    const lat1 = toRad(a[0]);
    const lat2 = toRad(b[0]);
    const x =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(lat1) * Math.cos(lat2);
    return 2 * R * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x));
  };

  const buildSimulatedQr = (seed: string, size = 17) => {
    let hash = 2166136261;
    for (let i = 0; i < seed.length; i += 1) {
      hash ^= seed.charCodeAt(i);
      hash +=
        (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
    }

    const rows: string[] = [];
    let state = Math.abs(hash) || 1;
    for (let r = 0; r < size; r += 1) {
      let row = '';
      for (let c = 0; c < size; c += 1) {
        state = (state * 1103515245 + 12345) & 0x7fffffff;
        row += state % 2 === 0 ? '█' : ' ';
      }
      rows.push(row);
    }
    return rows.join('\n');
  };

  const handleBuyTicket = async () => {
    if (!user) return;
    if (!ticketFromStop || !ticketToStop) {
      Alert.alert('Error', 'Please select source and destination stops.');
      return;
    }
    if (ticketFromStop.id === ticketToStop.id) {
      Alert.alert('Error', 'Source and destination cannot be the same.');
      return;
    }

    const distance = haversineKm(ticketFromStop.location, ticketToStop.location);
    const fare = user.is_senior ? 0 : Number((distance * TICKET_FARE_PER_KM).toFixed(2));

    if (!user.is_senior && user.balance < fare) {
      Alert.alert('Insufficient Balance', `Required Rs ${fare.toFixed(2)}. Please top up.`);
      return;
    }

    setTicketLoading(true);
    try {
      const ticketId = `TKT-${Date.now().toString().slice(-8)}`;
      const qrSeed = `${ticketId}|${ticketFromStop.name}|${ticketToStop.name}|${fare}`;
      const receipt: TicketReceipt = {
        ticket_id: ticketId,
        from_stop: ticketFromStop.name,
        to_stop: ticketToStop.name,
        distance_km: Number(distance.toFixed(2)),
        fare_rs: fare,
        issued_at: new Date().toLocaleString(),
        qr_code: buildSimulatedQr(qrSeed),
      };

      if (!user.is_senior) {
        setUser(prev => (prev ? {...prev, balance: Number((prev.balance - fare).toFixed(2))} : prev));
      }
      setTicketReceipt(receipt);
    } finally {
      setTicketLoading(false);
    }
  };

  const selectStop = (stop: Stop) => {
    if (selectingStop === 'from') {
      setFromStop(stop);
      setFromSearch(stop.name);
    } else {
      setToStop(stop);
      setToSearch(stop.name);
    }
    setSelectingStop(null);
    setJourneyResults(null);
  };

  const swapStops = () => {
    const tmp = fromStop;
    setFromStop(toStop);
    setToStop(tmp);
    setFromSearch(toStop?.name || '');
    setToSearch(fromStop?.name || '');
    setJourneyResults(null);
  };

  const injectJourneyBridge = () => {
    const js = `
      (function(){
        try {
          if (!window.__mobileJourneyBridgeInstalled) {
            window.__mobileJourneyBridgeInstalled = true;
            window.__jpPick = null; // 'from'|'to'|null
            window.__jpLayers = [];
            window.__jpColors = ['#ff006e','#3a86ff','#8338ec','#fb5607','#2ec4b6'];
            window.__jpFocusedRoutes = null; // object-as-set: { [routeId]: true }
            window.__jpHiddenRouteLayers = [];
            window.__jpHiddenStopLayers = [];
            window.__jpPendingFocus = null;
            window.__jpAgentLog = function(location, message, data, hypothesisId){
              // #region agent log
              fetch('http://127.0.0.1:7758/ingest/fd6c1564-db73-4909-83ad-a39909447a47',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'a6bc00'},body:JSON.stringify({sessionId:'a6bc00',runId:'run1',hypothesisId:hypothesisId,location:location,message:message,data:data,timestamp:Date.now()})}).catch(()=>{});
              // #endregion
            };

            function toKeySet(routeIds){
              var set = {};
              (routeIds||[]).forEach(function(r){ set[String(r)] = true; });
              return set;
            }

            function clearFocus() {
              window.__jpFocusedRoutes = null;
              try {
                window.__jpHiddenRouteLayers.forEach(function(l){
                  try { if (window.map && l && !window.map.hasLayer(l)) window.map.addLayer(l); } catch(e){}
                });
                window.__jpHiddenStopLayers.forEach(function(l){
                  try { if (window.map && l && !window.map.hasLayer(l)) window.map.addLayer(l); } catch(e){}
                });
              } catch(e){}
              window.__jpHiddenRouteLayers = [];
              window.__jpHiddenStopLayers = [];
            }

            function applyFocus(routeIds){
              if (!window.map) { window.__jpPendingFocus = routeIds; return; }
              try { window.__jpAgentLog('MapScreen.tsx:applyFocus:start','Applying focused routes',{routeIds:routeIds},'H2'); } catch(e){}
              clearFocus();
              window.__jpFocusedRoutes = toKeySet(routeIds);

              // Hide non-focused route polylines
              try {
                if (typeof routePolylines !== 'undefined' && routePolylines && routePolylines.forEach) {
                  var hiddenRouteCount = 0;
                  routePolylines.forEach(function(poly, routeId){
                    try {
                      if (!window.__jpFocusedRoutes[String(routeId)]) {
                        if (window.map.hasLayer(poly)) {
                          window.map.removeLayer(poly);
                          window.__jpHiddenRouteLayers.push(poly);
                          hiddenRouteCount += 1;
                        }
                      } else {
                        try { poly.bringToFront(); } catch(e){}
                      }
                    } catch(e){}
                  });
                  try { window.__jpAgentLog('MapScreen.tsx:applyFocus:routes','Route layers processed',{hiddenRouteCount:hiddenRouteCount,totalRouteLayers:routePolylines.size||null},'H2'); } catch(e){}
                }
              } catch(e){}

              // Hide non-focused stop groups
              try {
                if (typeof routeStopGroups !== 'undefined' && routeStopGroups && routeStopGroups.forEach) {
                  routeStopGroups.forEach(function(group, routeId){
                    try {
                      if (!window.__jpFocusedRoutes[String(routeId)]) {
                        if (window.map.hasLayer(group)) {
                          window.map.removeLayer(group);
                          window.__jpHiddenStopLayers.push(group);
                        }
                      }
                    } catch(e){}
                  });
                }
              } catch(e){}

              // Patch bus marker updates to only render focused-route buses
              try {
                if (!window.__jpOrigUpdateEnhancedBusMarkers && typeof updateEnhancedBusMarkers === 'function') {
                  window.__jpOrigUpdateEnhancedBusMarkers = updateEnhancedBusMarkers;
                  updateEnhancedBusMarkers = function(buses){
                    try {
                      if (window.__jpFocusedRoutes && Array.isArray(buses)) {
                        buses = buses.filter(function(b){ return window.__jpFocusedRoutes[String(b.route_id)]; });
                      }
                    } catch(e){}
                    return window.__jpOrigUpdateEnhancedBusMarkers(buses);
                  };
                }
              } catch(e){}

              // Immediately filter currently displayed bus markers
              try {
                if (typeof busMarkers !== 'undefined' && busMarkers && busMarkers.forEach && window.currentData && Array.isArray(window.currentData.buses)) {
                  var allowed = {};
                  window.currentData.buses.forEach(function(b){
                    if (window.__jpFocusedRoutes[String(b.route_id)]) allowed[String(b.bus_id)] = true;
                  });
                  busMarkers.forEach(function(marker, busId){
                    try {
                      if (!allowed[String(busId)] && window.map.hasLayer(marker)) {
                        window.map.removeLayer(marker);
                      }
                    } catch(e){}
                  });
                }
              } catch(e){}
            }

            window.__jpFocusRoutes = function(routeIds){
              if (!window.map || !window.map.whenReady) { window.__jpPendingFocus = routeIds; return; }
              window.map.whenReady(function(){ applyFocus(routeIds); });
            };
            window.__jpClearFocus = function(){
              if (!window.map || !window.map.whenReady) { window.__jpPendingFocus = null; return; }
              window.map.whenReady(function(){ clearFocus(); });
            };
            function clearLayers() {
              if (!window.map) return;
              window.__jpLayers.forEach(function(l){ try { window.map.removeLayer(l); } catch(e){} });
              window.__jpLayers = [];
            }
            window.__jpClear = clearLayers;
            window.__jpSetPick = function(mode){ window.__jpPick = mode; };
            window.__jpPendingJourney = null;
            function doDraw(journey){
              if (!window.map) { window.__jpPendingJourney = journey; return; }
              clearLayers();
              if (!journey || !Array.isArray(journey.segments)) return;
              try { window.__jpAgentLog('MapScreen.tsx:doDraw:start','Drawing journey',{segmentsCount:journey.segments?journey.segments.length:0},'H3'); } catch(e){}
              // Overall A → B markers
              try {
                var firstSeg = journey.segments[0];
                var lastSeg = journey.segments[journey.segments.length - 1];
                if (firstSeg && lastSeg) {
                  var aIcon = L.divIcon({className:'',html:'<div style="background:#28a745;color:#fff;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-weight:800;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.35);">A</div>',iconSize:[28,28]});
                  var bIcon = L.divIcon({className:'',html:'<div style="background:#dc3545;color:#fff;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-weight:800;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.35);">B</div>',iconSize:[28,28]});
                  var a = L.marker([firstSeg.board_location[0], firstSeg.board_location[1]], {icon: aIcon}).addTo(window.map);
                  var b = L.marker([lastSeg.alight_location[0], lastSeg.alight_location[1]], {icon: bIcon}).addTo(window.map);
                  window.__jpLayers.push(a); window.__jpLayers.push(b);
                }
              } catch(e) {}
              journey.segments.forEach(function(seg, idx){
                var color = window.__jpColors[idx % window.__jpColors.length];
                var coords = [
                  [seg.board_location[0], seg.board_location[1]],
                  [seg.alight_location[0], seg.alight_location[1]]
                ];
                try {
                  if (window.currentData && window.currentData.routes && window.currentData.routes[seg.route_id] && window.currentData.routes[seg.route_id].stops) {
                    var stops = window.currentData.routes[seg.route_id].stops;
                    var norm = function(v){ return String(v||'').trim().toLowerCase(); };
                    var b = norm(seg.board_stop), a = norm(seg.alight_stop);
                    var bi = stops.findIndex(function(s){ return norm(s.name)===b; });
                    var ai = stops.findIndex(function(s){ return norm(s.name)===a; });
                    if (bi>=0 && ai>=0 && bi!==ai) {
                      var start = Math.min(bi,ai), end = Math.max(bi,ai);
                      coords = stops.slice(start,end+1).map(function(s){ return [s.latitude,s.longitude]; });
                      if (bi>ai) coords.reverse();
                    }
                  }
                } catch(e){}
                if (idx === 0) {
                  try { window.__jpAgentLog('MapScreen.tsx:doDraw:firstSegment','First segment coordinates prepared',{routeId:seg.route_id,coordsCount:coords?coords.length:0,board:seg.board_stop,alight:seg.alight_stop},'H4'); } catch(e){}
                }
                // Bold highlight: white outline under colored line
                var outline = L.polyline(coords,{color:'#ffffff',weight:18,opacity:0.98,lineCap:'round',lineJoin:'round',dashArray:(idx>0?'8,8':null)}).addTo(window.map);
                var line = L.polyline(coords,{color:color,weight:13,opacity:1,lineCap:'round',lineJoin:'round',dashArray:(idx>0?'8,8':null)}).addTo(window.map);
                try { outline.bringToFront(); line.bringToFront(); } catch(e){}
                window.__jpLayers.push(outline);
                window.__jpLayers.push(line);
                var bmk = L.circleMarker([seg.board_location[0], seg.board_location[1]],{radius:6,color:'#fff',weight:2,fillColor:color,fillOpacity:1}).addTo(window.map);
                var amk = L.circleMarker([seg.alight_location[0], seg.alight_location[1]],{radius:6,color:'#fff',weight:2,fillColor:color,fillOpacity:1}).addTo(window.map);
                window.__jpLayers.push(bmk); window.__jpLayers.push(amk);
              });
              try {
                var all = journey.segments.flatMap(function(s){ return [[s.board_location[0],s.board_location[1]],[s.alight_location[0],s.alight_location[1]]];});
                if (all.length) {
                  window.map.fitBounds(L.latLngBounds(all).pad(0.2));
                  try { window.__jpAgentLog('MapScreen.tsx:doDraw:fitBounds','fitBounds executed',{pointsCount:all.length},'H5'); } catch(e){}
                } else {
                  try { window.__jpAgentLog('MapScreen.tsx:doDraw:fitBounds','fitBounds skipped due empty points',{pointsCount:0},'H5'); } catch(e){}
                }
              } catch(e){}
            }
            window.__jpDraw = function(journey){
              // If map isn't ready yet, queue and draw when ready.
              if (!window.map || !window.map.whenReady) { window.__jpPendingJourney = journey; return; }
              window.map.whenReady(function(){ doDraw(journey); });
            };
            window.__jpGoToStart = function(journey){
              if (!journey || !Array.isArray(journey.segments) || !journey.segments.length) return;
              var firstSeg = journey.segments[0];
              var lat = firstSeg.board_location && firstSeg.board_location[0];
              var lng = firstSeg.board_location && firstSeg.board_location[1];
              if (typeof lat !== 'number' || typeof lng !== 'number') return;
              var run = function(){
                try {
                  if (!window.map) return;
                  window.map.setView([lat, lng], 16, {animate: true});
                  var icon = L.divIcon({className:'',html:'<div style="background:#28a745;color:#fff;border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-weight:800;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.35);">A</div>',iconSize:[30,30]});
                  var mk = L.marker([lat,lng],{icon:icon}).addTo(window.map);
                  var txt = 'Start at ' + firstSeg.board_stop + '. Take ' + firstSeg.route_id + ' towards ' + firstSeg.alight_stop + '.';
                  mk.bindPopup(txt).openPopup();
                  if (!window.__jpLayers) window.__jpLayers = [];
                  window.__jpLayers.push(mk);
                } catch(e){}
              };
              if (window.map && window.map.whenReady) {
                window.map.whenReady(function(){
                  run();
                  setTimeout(run, 120);
                  setTimeout(run, 300);
                });
              } else {
                run();
                setTimeout(run, 120);
                setTimeout(run, 300);
              }
            };
            // If something queued before bridge was installed, draw it now.
            try {
              if (window.map && window.__jpPendingJourney) {
                window.map.whenReady(function(){ doDraw(window.__jpPendingJourney); window.__jpPendingJourney = null; });
              }
              if (window.map && window.__jpPendingFocus) {
                window.map.whenReady(function(){ applyFocus(window.__jpPendingFocus); window.__jpPendingFocus = null; });
              }
            } catch(e) {}
            if (window.map && window.map.on) {
              window.map.on('click', function(e){
                try {
                  if (!window.__jpPick) return;
                  var payload = { type: 'journey_pick', pick: window.__jpPick, lat: e.latlng.lat, lng: e.latlng.lng };
                  if (window.ReactNativeWebView && window.ReactNativeWebView.postMessage) {
                    window.ReactNativeWebView.postMessage(JSON.stringify(payload));
                  }
                } catch(err){}
              });
            }
          }
        } catch(e){}
      })();
      true;
    `;
    webviewRef.current?.injectJavaScript(js);
  };

  const setPickModeOnMap = (pick: 'from' | 'to' | null) => {
    const js = `try{ if(window.__jpSetPick) window.__jpSetPick(${pick ? `'${pick}'` : 'null'}); }catch(e){}; true;`;
    webviewRef.current?.injectJavaScript(js);
  };

  const drawJourneyOnMap = (journey: JourneyOption) => {
    const js = `try{ if(window.__jpDraw) window.__jpDraw(${JSON.stringify(journey)}); }catch(e){}; true;`;
    webviewRef.current?.injectJavaScript(js);
  };

  const focusRoutesOnMap = (routeIds: string[]) => {
    const js = `try{ if(window.__jpFocusRoutes) window.__jpFocusRoutes(${JSON.stringify(routeIds)}); }catch(e){}; true;`;
    webviewRef.current?.injectJavaScript(js);
  };

  const selectJourneyOnMap = (journey: JourneyOption, routeIds: string[]) => {
    const js = `
      (function(){
        try {
          var __journey = ${JSON.stringify(journey)};
          var __routeIds = ${JSON.stringify(routeIds)};
          var run = function() {
            try {
              if (typeof visualizeJourneyOnMap === 'function') {
                visualizeJourneyOnMap(__journey);
              }
              if (window.__jpFocusRoutes) window.__jpFocusRoutes(__routeIds);
              if (window.__jpDraw) window.__jpDraw(__journey);
              if (window.map && window.map.invalidateSize) window.map.invalidateSize();
            } catch(e) {}
          };
          if (window.map && window.map.whenReady) {
            window.map.whenReady(function(){
              run();
              setTimeout(run, 120);
              setTimeout(run, 300);
            });
          } else {
            run();
            setTimeout(run, 120);
            setTimeout(run, 300);
          }
        } catch(e) {}
      })();
      true;
    `;
    webviewRef.current?.injectJavaScript(js);
  };

  const handleSelectJourney = (journey: JourneyOption) => {
    const routeIds = Array.from(new Set(journey.segments.map(s => s.route_id)));
    // Hide native route lines so only bold selected journey remains.
    setShowRoutesLayer(false);
    setShowLayerPopup(false);
    applyDisplayLayers(showFleetLayer, false, showStationsLayer, showTrafficLayer);
    selectJourneyOnMap(journey, routeIds);
    setSelectedJourney(journey);
    setShowJourneySteps(false);
    // Close planner so map is fully visible
    setActiveModal(null);
  };

  const handleStartJourney = () => {
    if (!selectedJourney || !selectedJourney.segments?.length) return;
    const routeIds = Array.from(new Set(selectedJourney.segments.map(s => s.route_id)));
    const js = `
      (function(){
        try {
          var j = ${JSON.stringify(selectedJourney)};
          var r = ${JSON.stringify(routeIds)};
          if (window.__jpFocusRoutes) window.__jpFocusRoutes(r);
          if (window.__jpDraw) window.__jpDraw(j);
          if (window.__jpGoToStart) window.__jpGoToStart(j);
        } catch(e){}
      })();
      true;
    `;
    webviewRef.current?.injectJavaScript(js);
    setShowJourneySteps(true);
  };

  const hideWebUI = () => {
    const jsCode = `
      (function() {
        setTimeout(function() {
          var elementsToHide = ['.header','.department-info','.stats-container','.control-panel','.eticket-button','button:not(.leaflet-control button)'];
          elementsToHide.forEach(function(selector) {
            var elements = document.querySelectorAll(selector);
            elements.forEach(function(el) {
              if (!el.classList.contains('leaflet-control') && !el.closest('.leaflet-control') && el.id !== 'map') {
                el.style.display = 'none';
              }
            });
          });
          var allDivs = document.querySelectorAll('div');
          allDivs.forEach(function(div) {
            var style = window.getComputedStyle(div);
            if (style.position === 'absolute' && div.id !== 'map' && !div.classList.contains('leaflet-control') && !div.closest('.leaflet-control') && !div.closest('#map')) {
              div.style.display = 'none';
            }
          });
          var mapEl = document.getElementById('map');
          if (mapEl) { mapEl.style.position='fixed'; mapEl.style.top='0'; mapEl.style.left='0'; mapEl.style.width='100vw'; mapEl.style.height='100vh'; mapEl.style.zIndex='1'; }
          document.body.style.margin='0'; document.body.style.padding='0'; document.body.style.overflow='hidden';
          if (window.map && window.map.invalidateSize) window.map.invalidateSize();
        }, 500);
      })();
      true;
    `;
    webviewRef.current?.injectJavaScript(jsCode);
    injectJourneyBridge();
  };

  const handleWebViewMessage = (event: any) => {
    try {
      const msg = JSON.parse(event.nativeEvent.data);
      if (msg?.type === 'journey_pick' && msg?.lat && msg?.lng) {
        if (msg.pick === 'from') {
          setFromPoint([msg.lat, msg.lng]);
          setSelectingPoint(null);
          setPickModeOnMap(null);
        } else if (msg.pick === 'to') {
          setToPoint([msg.lat, msg.lng]);
          setSelectingPoint(null);
          setPickModeOnMap(null);
        }
      }
    } catch (e) {
      // ignore
    }
  };

  const applyDisplayLayers = (
    nextFleet: boolean,
    nextRoutes: boolean,
    nextStations: boolean,
    nextTraffic: boolean,
  ) => {
    const js = `
      (function(){
        try {
          if (typeof showBuses !== 'undefined' && typeof toggleBuses === 'function' && showBuses !== ${nextFleet}) toggleBuses();
          if (typeof showRoutes !== 'undefined' && typeof toggleRoutes === 'function' && showRoutes !== ${nextRoutes}) toggleRoutes();
          if (typeof showStops !== 'undefined' && typeof toggleStops === 'function' && showStops !== ${nextStations}) toggleStops();
          if (typeof showTraffic !== 'undefined' && typeof toggleTraffic === 'function' && showTraffic !== ${nextTraffic}) toggleTraffic();
        } catch(e) {}
      })();
      true;
    `;
    webviewRef.current?.injectJavaScript(js);
  };

  const handleToggleFleet = () => {
    const next = !showFleetLayer;
    setShowFleetLayer(next);
    applyDisplayLayers(next, showRoutesLayer, showStationsLayer, showTrafficLayer);
  };

  const handleToggleRoutes = () => {
    const next = !showRoutesLayer;
    setShowRoutesLayer(next);
    applyDisplayLayers(showFleetLayer, next, showStationsLayer, showTrafficLayer);
  };

  const handleToggleStations = () => {
    const next = !showStationsLayer;
    setShowStationsLayer(next);
    applyDisplayLayers(showFleetLayer, showRoutesLayer, next, showTrafficLayer);
  };

  const handleToggleTraffic = () => {
    const next = !showTrafficLayer;
    setShowTrafficLayer(next);
    applyDisplayLayers(showFleetLayer, showRoutesLayer, showStationsLayer, next);
  };

  if (loading) {
    return (
      <View style={s.center}>
        <ActivityIndicator size="large" color="#1565C0" />
        <Text style={s.loadTxt}>Loading Metro Buses...</Text>
      </View>
    );
  }

  const finalAmount = customAmount ? parseInt(customAmount) : selectedAmount;
  const currentSearch = selectingStop === 'from'
    ? fromSearch
    : selectingStop === 'to'
      ? toSearch
      : ticketSelectingStop === 'from'
        ? ticketFromSearch
        : ticketToSearch;

  return (
    <View style={s.container}>
      <WebView
        ref={webviewRef}
        source={{uri: `${API_URL}/map`}}
        style={{flex: 1, backgroundColor: '#e0e0e0'}}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        startInLoadingState={true}
        onLoadEnd={hideWebUI}
        onMessage={handleWebViewMessage}
        onLoad={() => {
          setTimeout(() => {
            webviewRef.current?.injectJavaScript(`if (window.map && window.map.invalidateSize) window.map.invalidateSize(); true;`);
          }, 1000);
        }}
        renderLoading={() => (
          <View style={s.center}>
            <ActivityIndicator size="large" color="#1565C0" />
            <Text style={s.loadTxt}>Loading Map...</Text>
          </View>
        )}
      />

      {/* Top Bar */}
      <View style={s.topBar}>
        <Text style={s.topTitle}>🚌 Metro Live</Text>
        <TouchableOpacity style={s.refreshBtn} onPress={fetchBuses}>
          <Text style={s.refreshTxt}>🔄</Text>
        </TouchableOpacity>
      </View>

      {/* FABs */}
      <View style={s.fabContainer}>
        <TouchableOpacity style={[s.fab, activeModal === 'list' && s.fabActive]} onPress={() => openModal('list')}>
          <Text style={s.fabIcon}>📋</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[s.fab, activeModal === 'journey' && s.fabActive]} onPress={() => openModal('journey')}>
          <Text style={s.fabIcon}>🗺️</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[s.fab, activeModal === 'eticket' && s.fabActive]} onPress={() => openModal('eticket')}>
          <Text style={s.fabIcon}>🎫</Text>
        </TouchableOpacity>
      </View>

      {/* Bottom Display Layers Popup */}
      <View style={s.layersDock}>
        {showLayerPopup && (
          <View style={s.layersPopup}>
            <Text style={s.layersTitle}>Display Layers</Text>
            <View style={s.layersRow}>
              <TouchableOpacity
                style={[s.layerChip, showFleetLayer && s.layerChipActive]}
                onPress={handleToggleFleet}>
                <Text style={[s.layerChipText, showFleetLayer && s.layerChipTextActive]}>Fleet</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[s.layerChip, showRoutesLayer && s.layerChipActive]}
                onPress={handleToggleRoutes}>
                <Text style={[s.layerChipText, showRoutesLayer && s.layerChipTextActive]}>Routes</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[s.layerChip, showStationsLayer && s.layerChipActive]}
                onPress={handleToggleStations}>
                <Text style={[s.layerChipText, showStationsLayer && s.layerChipTextActive]}>Stations</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[s.layerChip, showTrafficLayer && s.layerChipActive]}
                onPress={handleToggleTraffic}>
                <Text style={[s.layerChipText, showTrafficLayer && s.layerChipTextActive]}>Traffic</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
        <TouchableOpacity
          style={s.layersToggleBtn}
          onPress={() => setShowLayerPopup(v => !v)}>
          <Text style={s.layersToggleIcon}>{showLayerPopup ? '✕' : '🧭'}</Text>
        </TouchableOpacity>
      </View>

      {/* Start journey CTA (shown after route selection) */}
      {selectedJourney && activeModal === null && (
        <View style={s.startJourneyDock}>
          <TouchableOpacity style={s.startJourneyBtn} onPress={handleStartJourney}>
            <Text style={s.startJourneyBtnTxt}>▶ Start Journey</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Journey steps panel */}
      {showJourneySteps && selectedJourney && (
        <View style={s.stepsOverlay}>
          <View style={s.stepsPanel}>
            <View style={s.stepsHeader}>
              <Text style={s.stepsTitle}>Next Steps</Text>
              <View style={s.stepsHeaderActions}>
                <TouchableOpacity style={s.stepsStartBtn} onPress={handleStartJourney}>
                  <Text style={s.stepsStartBtnTxt}>Go to Start</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => setShowJourneySteps(false)}>
                  <Text style={s.stepsClose}>✕</Text>
                </TouchableOpacity>
              </View>
            </View>
            <ScrollView style={{maxHeight: 220}}>
              {selectedJourney.instructions.map(step => (
                <View key={`${selectedJourney.journey_id}_${step.step}`} style={s.stepRow}>
                  <View style={s.stepNo}><Text style={s.stepNoTxt}>{step.step}</Text></View>
                  <Text style={s.stepTxt}>{step.instruction}</Text>
                </View>
              ))}
            </ScrollView>
          </View>
        </View>
      )}

      {/* Bottom Sheet Modal */}
      {activeModal !== null && (
        <View style={s.modalOverlay}>
          <TouchableOpacity style={{flex: 1}} activeOpacity={1} onPress={closeModal} />
          <View style={s.modalContentInner}>
            <View style={s.modalHeader}>
              <View style={s.modalHandle} />
              {(showTopup || selectingStop || ticketSelectingStop) ? (
                <TouchableOpacity style={s.backBtn} onPress={() => { setShowTopup(false); setSelectingStop(null); setTicketSelectingStop(null); }}>
                  <Text style={s.backTxt}>← Back</Text>
                </TouchableOpacity>
              ) : (
                <View style={{width: 60}} />
              )}
              <Text style={s.modalTitle}>
                {activeModal === 'list' ? '📋 Bus List' :
                 activeModal === 'journey' ? (selectingStop ? `Select ${selectingStop === 'from' ? 'From' : 'To'} Stop` : '🗺️ Journey Planner') :
                 activeModal === 'eticket' && ticketSelectingStop ? `Select ${ticketSelectingStop === 'from' ? 'Source' : 'Destination'} Stop` :
                 showTopup ? '💳 Top Up' : '🎫 E-Ticket'}
              </Text>
              <TouchableOpacity style={s.closeBtn} onPress={closeModal}>
                <Text style={s.closeTxt}>✕</Text>
              </TouchableOpacity>
            </View>

            {/* STOP SELECTOR */}
            {(activeModal === 'journey' && selectingStop) || (activeModal === 'eticket' && ticketSelectingStop) ? (
              <View style={{flex: 1}}>
                <View style={s.searchBox}>
                  <TextInput
                    style={s.searchInput}
                    placeholder={`Search ${(activeModal === 'journey' ? selectingStop : ticketSelectingStop) === 'from' ? 'source' : 'destination'} stop...`}
                    placeholderTextColor="#aaa"
                    value={currentSearch}
                    onChangeText={val => {
                      const target = activeModal === 'journey' ? selectingStop : ticketSelectingStop;
                      if (activeModal === 'journey') {
                        target === 'from' ? setFromSearch(val) : setToSearch(val);
                      } else {
                        target === 'from' ? setTicketFromSearch(val) : setTicketToSearch(val);
                      }
                    }}
                    autoFocus
                  />
                </View>
                {stopsLoading ? (
                  <View style={s.center}>
                    <ActivityIndicator size="small" color="#1565C0" />
                    <Text style={{color: '#888', marginTop: 8}}>Loading stops...</Text>
                  </View>
                ) : (
                  <FlatList
                    data={filteredStops(currentSearch)}
                    keyExtractor={item => item.id}
                    renderItem={({item}) => (
                      <TouchableOpacity style={s.stopItem} onPress={() => {
                        if (activeModal === 'journey') {
                          selectStop(item);
                        } else if (ticketSelectingStop === 'from') {
                          setTicketFromStop(item);
                          setTicketFromSearch(item.name);
                          setTicketSelectingStop(null);
                          setTicketReceipt(null);
                        } else {
                          setTicketToStop(item);
                          setTicketToSearch(item.name);
                          setTicketSelectingStop(null);
                          setTicketReceipt(null);
                        }
                      }}>
                        <View>
                          <Text style={s.stopName}>{item.name}</Text>
                          <Text style={s.stopRoutes}>
                            Routes: {item.connected_routes.join(', ')}
                          </Text>
                        </View>
                        <Text style={s.stopArrow}>›</Text>
                      </TouchableOpacity>
                    )}
                    ItemSeparatorComponent={() => <View style={{height: 1, backgroundColor: '#f0f0f0'}} />}
                    ListEmptyComponent={
                      <View style={s.emptyState}>
                        <Text style={s.emptyText}>No stops found</Text>
                        <Text style={s.emptySubtext}>Try a different search term</Text>
                      </View>
                    }
                  />
                )}
              </View>
            ) : null}

            {/* JOURNEY PLANNER MAIN */}
            {activeModal === 'journey' && !selectingStop && (
              <ScrollView style={s.modalBody} contentContainerStyle={{paddingBottom: 20}}>
                <Text style={s.journeySubtitle}>Plan journeys like the web Journey Planner</Text>

                {/* Mode toggle */}
                <View style={s.toggleRow}>
                  <TouchableOpacity
                    style={[s.toggleBtn, journeyMode === 'stops' && s.toggleBtnActive]}
                    onPress={() => {
                      setJourneyMode('stops');
                      setSelectingPoint(null);
                      setPickModeOnMap(null);
                      setJourneyResults(null);
                      setJourneyError('');
                    }}>
                    <Text style={[s.toggleTxt, journeyMode === 'stops' && s.toggleTxtActive]}>Stop Selection</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[s.toggleBtn, journeyMode === 'map' && s.toggleBtnActive]}
                    onPress={() => {
                      setJourneyMode('map');
                      setSelectingStop(null);
                      setJourneyResults(null);
                      setJourneyError('');
                    }}>
                    <Text style={[s.toggleTxt, journeyMode === 'map' && s.toggleTxtActive]}>Map Selection</Text>
                  </TouchableOpacity>
                </View>

                {journeyMode === 'stops' ? (
                  <>
                    {/* FROM */}
                    <Text style={s.label}>📍 Origin Stop</Text>
                    <TouchableOpacity
                      style={[s.stopSelector, fromStop && s.stopSelectorFilled]}
                      onPress={() => { setSelectingStop('from'); setFromSearch(fromStop?.name || ''); }}>
                      <Text style={fromStop ? s.stopSelectorTxt : s.stopSelectorPlaceholder}>
                        {fromStop ? fromStop.name : 'Tap to select origin stop'}
                      </Text>
                      <Text style={s.dropdownArrow}>▼</Text>
                    </TouchableOpacity>

                    {/* SWAP */}
                    <TouchableOpacity style={s.swapBtn} onPress={swapStops}>
                      <Text style={s.swapTxt}>⇅ Swap</Text>
                    </TouchableOpacity>

                    {/* TO */}
                    <Text style={s.label}>🏁 Destination Stop</Text>
                    <TouchableOpacity
                      style={[s.stopSelector, toStop && s.stopSelectorFilled]}
                      onPress={() => { setSelectingStop('to'); setToSearch(toStop?.name || ''); }}>
                      <Text style={toStop ? s.stopSelectorTxt : s.stopSelectorPlaceholder}>
                        {toStop ? toStop.name : 'Tap to select destination stop'}
                      </Text>
                      <Text style={s.dropdownArrow}>▼</Text>
                    </TouchableOpacity>
                  </>
                ) : (
                  <>
                    <Text style={s.label}>📍 Origin Point</Text>
                    <TouchableOpacity
                      style={[s.pointBtn, selectingPoint === 'from' && s.pointBtnActive]}
                      onPress={() => {
                        setSelectingPoint('from');
                        setPickModeOnMap('from');
                      }}>
                      <Text style={s.pointBtnTxt}>
                        {fromPoint ? `${fromPoint[0].toFixed(5)}, ${fromPoint[1].toFixed(5)}` : 'Tap map to set origin'}
                      </Text>
                    </TouchableOpacity>

                    <Text style={s.label}>🏁 Destination Point</Text>
                    <TouchableOpacity
                      style={[s.pointBtn, selectingPoint === 'to' && s.pointBtnActive]}
                      onPress={() => {
                        setSelectingPoint('to');
                        setPickModeOnMap('to');
                      }}>
                      <Text style={s.pointBtnTxt}>
                        {toPoint ? `${toPoint[0].toFixed(5)}, ${toPoint[1].toFixed(5)}` : 'Tap map to set destination'}
                      </Text>
                    </TouchableOpacity>
                    <Text style={s.hintTxt}>When a point mode is active, tap on the map to pick the coordinate.</Text>
                  </>
                )}

                {/* Max transfers */}
                <Text style={s.label}>🔁 Max Transfers</Text>
                <View style={s.inlineRow}>
                  {[0, 1, 2, 3].map(n => (
                    <TouchableOpacity
                      key={n}
                      style={[s.chip, maxTransfers === n && s.chipActive]}
                      onPress={() => setMaxTransfers(n)}>
                      <Text style={[s.chipTxt, maxTransfers === n && s.chipTxtActive]}>{n}</Text>
                    </TouchableOpacity>
                  ))}
                </View>

                {/* Preference */}
                <Text style={s.label}>⚙️ Preference</Text>
                <View style={s.inlineRow}>
                  <TouchableOpacity style={[s.chip, preference === 'time' && s.chipActive]} onPress={() => setPreference('time')}>
                    <Text style={[s.chipTxt, preference === 'time' && s.chipTxtActive]}>Time</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[s.chip, preference === 'money' && s.chipActive]} onPress={() => setPreference('money')}>
                    <Text style={[s.chipTxt, preference === 'money' && s.chipTxtActive]}>Money</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[s.chip, preference === 'hybrid' && s.chipActive]} onPress={() => setPreference('hybrid')}>
                    <Text style={[s.chipTxt, preference === 'hybrid' && s.chipTxtActive]}>Hybrid</Text>
                  </TouchableOpacity>
                </View>

                <TouchableOpacity
                  style={[
                    s.planBtn,
                    ((journeyMode === 'stops' && (!fromStop || !toStop)) || (journeyMode === 'map' && (!fromPoint || !toPoint)) || journeyLoading) && s.planBtnDisabled
                  ]}
                  onPress={handlePlanJourney}
                  disabled={(journeyMode === 'stops' && (!fromStop || !toStop)) || (journeyMode === 'map' && (!fromPoint || !toPoint)) || journeyLoading}>
                  {journeyLoading ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={s.planBtnTxt}>🔍 FIND ROUTES</Text>
                  )}
                </TouchableOpacity>

                {/* ERROR */}
                {journeyError ? (
                  <View style={s.errorBox}>
                    <Text style={s.errorEmoji}>😕</Text>
                    <Text style={s.errorTxt}>{journeyError}</Text>
                    <Text style={s.errorHint}>Try selecting different stops</Text>
                  </View>
                ) : null}

                {/* RESULTS */}
                {journeyResults && journeyResults.length > 0 && (
                  <View style={s.resultsContainer}>
                    <Text style={s.resultsTitle}>
                      ✅ {journeyResults.length} Route{journeyResults.length > 1 ? 's' : ''} Found
                    </Text>
                    <Text style={s.resultsSubtitle}>Top 5 results • Tap a card to expand • Tap Select to draw on map</Text>

                    {journeyResults.map((option, i) => (
                      <View key={option.journey_id} style={[s.resultCard, i === 0 && s.resultCardBest]}>
                        {i === 0 && (
                          <View style={s.bestBadge}>
                            <Text style={s.bestBadgeTxt}>⭐ BEST</Text>
                          </View>
                        )}

                        <TouchableOpacity
                          onPress={() => setExpandedJourneyId(prev => prev === option.journey_id ? null : option.journey_id)}
                          activeOpacity={0.8}
                        >
                          <Text style={s.resultRouteName}>🚌 {option.route_names.join(' → ')}</Text>
                          <View style={s.routePathRow}>
                            <Text style={s.routeFrom} numberOfLines={1}>
                              {journeyMode === 'stops' ? fromStop?.name : 'Origin'}
                            </Text>
                            <Text style={s.routeArrow}> → </Text>
                            <Text style={s.routeTo} numberOfLines={1}>
                              {journeyMode === 'stops' ? toStop?.name : 'Destination'}
                            </Text>
                          </View>
                        </TouchableOpacity>

                        {/* Stats */}
                        <View style={s.statsRow}>
                          <View style={s.statChip}>
                            <Text style={s.statEmoji}>📏</Text>
                            <Text style={s.statVal}>{Number(option.summary.total_distance_km).toFixed(1)} km</Text>
                            <Text style={s.statLbl}>Distance</Text>
                          </View>
                          <View style={s.statChip}>
                            <Text style={s.statEmoji}>⏱️</Text>
                            <Text style={s.statVal}>{Math.round(option.summary.estimated_total_time_minutes)} min</Text>
                            <Text style={s.statLbl}>Time</Text>
                          </View>
                          <View style={s.statChip}>
                            <Text style={s.statEmoji}>💰</Text>
                            <Text style={s.statVal}>Rs {Number(option.summary.total_fare_rs).toFixed(0)}</Text>
                            <Text style={s.statLbl}>Fare</Text>
                          </View>
                          <View style={s.statChip}>
                            <Text style={s.statEmoji}>🔄</Text>
                            <Text style={s.statVal}>{option.summary.transfers_required}</Text>
                            <Text style={s.statLbl}>Transfers</Text>
                          </View>
                        </View>

                        <View style={s.actionsRow}>
                          <TouchableOpacity
                            style={s.selectBtn}
                            onPress={() => handleSelectJourney(option)}>
                            <Text style={s.selectBtnTxt}>Select</Text>
                          </TouchableOpacity>
                        </View>

                        {/* Expandable details */}
                        {expandedJourneyId === option.journey_id && (
                          <View style={s.segmentsBox}>
                            {option.segments.map((seg, j) => (
                              <View key={`${option.journey_id}_seg_${j}`} style={s.segRow}>
                                <View style={s.segDot} />
                                <Text style={s.segTxt}>
                                  Leg {j + 1}: {seg.route_id} • {seg.board_stop} → {seg.alight_stop} • {seg.distance_km} km • Rs {seg.fare_rs}
                                </Text>
                              </View>
                            ))}
                            <View style={{height: 8}} />
                            {option.instructions.map(step => (
                              <View key={`${option.journey_id}_step_${step.step}`} style={s.segRow}>
                                <View style={[s.segDot, {backgroundColor: '#6c757d'}]} />
                                <Text style={s.segTxt}>{step.step}. {step.instruction}</Text>
                              </View>
                            ))}
                          </View>
                        )}
                      </View>
                    ))}
                  </View>
                )}
              </ScrollView>
            )}

            {/* BUS LIST */}
            {activeModal === 'list' && (
              <ScrollView style={s.modalBody} contentContainerStyle={{paddingBottom: 20}}>
                <View style={s.busCountBox}>
                  <Text style={s.busCountTxt}>Active Buses: {buses.length}</Text>
                  <Text style={s.busUpdateTxt}>Last Update: {lastUpdate}</Text>
                </View>
                {buses.length === 0 ? (
                  <View style={s.emptyState}>
                    <Text style={s.emptyText}>No active buses</Text>
                    <Text style={s.emptySubtext}>Activate buses from web admin panel</Text>
                  </View>
                ) : (
                  buses.map((bus, i) => (
                    <View key={i} style={s.card}>
                      <View style={s.cardHead}>
                        <Text style={s.cardId}>{bus.bus_id}</Text>
                        <View style={[s.badge, bus.bus_id?.includes('-F-') ? s.fBadge : s.rBadge]}>
                          <Text style={s.badgeTxt}>{bus.bus_id?.includes('-F-') ? '▶ FWD' : '◀ REV'}</Text>
                        </View>
                      </View>
                      <Text style={s.cardRoute}>Route: {bus.route_id}</Text>
                      {bus.speed != null && <Text style={s.cardSpeed}>⚡ {Number(bus.speed).toFixed(1)} km/h</Text>}
                      <Text style={s.cardCoord}>📍 {bus.current_lat?.toFixed(4)}, {bus.current_lng?.toFixed(4)}</Text>
                    </View>
                  ))
                )}
              </ScrollView>
            )}

            {/* E-TICKET */}
            {activeModal === 'eticket' && (
              <ScrollView style={s.modalBody} contentContainerStyle={{paddingBottom: 20}}>
                {!user && (
                  <View style={s.eticketContainer}>
                    <Text style={s.eticketTitle}>Purchase Metro Bus E-Ticket</Text>
                    <TouchableOpacity style={s.eticketBtn} onPress={() => setAuthScreen('login')}>
                      <Text style={s.eticketBtnTxt}>Login / Sign Up</Text>
                    </TouchableOpacity>
                    <Text style={s.eticketInfo}>🎉 Senior citizens (60+) travel FREE!</Text>
                    <View style={s.infoBox}>
                      <Text style={s.infoText}>💳 Top-up: EasyPaisa, JazzCash, NayaPay, SadaPay</Text>
                      <Text style={s.infoText}>💰 Fare: Rs. 3/km</Text>
                    </View>
                  </View>
                )}

                {user && !showTopup && (
                  <View>
                    {user.is_senior && (
                      <View style={s.seniorBanner}>
                        <Text style={s.seniorBannerTxt}>🎉 Senior Citizen - FREE Travel!</Text>
                      </View>
                    )}
                    <View style={s.walletCard}>
                      <Text style={s.walletGreeting}>Hello, {user.name}! 👋</Text>
                      <Text style={s.walletLabel}>Wallet Balance</Text>
                      <Text style={s.walletBalance}>Rs. {Number(user.balance).toFixed(2)}</Text>
                    </View>
                    <TouchableOpacity style={s.topupBtn} onPress={() => setShowTopup(true)}>
                      <Text style={s.topupBtnTxt}>💳 Top Up Wallet</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={s.logoutBtn} onPress={handleLogout}>
                      <Text style={s.logoutBtnTxt}>Logout</Text>
                    </TouchableOpacity>

                    {/* Ticket purchase */}
                    <View style={s.ticketSection}>
                      <Text style={s.ticketSectionTitle}>Create Ticket</Text>

                      <Text style={s.label}>📍 Source Stop</Text>
                      <TouchableOpacity
                        style={[s.stopSelector, ticketFromStop && s.stopSelectorFilled]}
                        onPress={() => {
                          setTicketSelectingStop('from');
                          setTicketFromSearch(ticketFromStop?.name || '');
                        }}>
                        <Text style={ticketFromStop ? s.stopSelectorTxt : s.stopSelectorPlaceholder}>
                          {ticketFromStop ? ticketFromStop.name : 'Select source stop'}
                        </Text>
                        <Text style={s.dropdownArrow}>▼</Text>
                      </TouchableOpacity>

                      <Text style={s.label}>🏁 Destination Stop</Text>
                      <TouchableOpacity
                        style={[s.stopSelector, ticketToStop && s.stopSelectorFilled]}
                        onPress={() => {
                          setTicketSelectingStop('to');
                          setTicketToSearch(ticketToStop?.name || '');
                        }}>
                        <Text style={ticketToStop ? s.stopSelectorTxt : s.stopSelectorPlaceholder}>
                          {ticketToStop ? ticketToStop.name : 'Select destination stop'}
                        </Text>
                        <Text style={s.dropdownArrow}>▼</Text>
                      </TouchableOpacity>

                      {ticketFromStop && ticketToStop && (
                        <Text style={s.ticketFarePreview}>
                          Distance: {haversineKm(ticketFromStop.location, ticketToStop.location).toFixed(2)} km •
                          Fare: Rs {(user.is_senior ? 0 : haversineKm(ticketFromStop.location, ticketToStop.location) * TICKET_FARE_PER_KM).toFixed(2)}
                        </Text>
                      )}

                      <TouchableOpacity
                        style={[s.confirmBtn, (!ticketFromStop || !ticketToStop || ticketLoading) && s.confirmBtnDisabled]}
                        onPress={handleBuyTicket}
                        disabled={!ticketFromStop || !ticketToStop || ticketLoading}>
                        {ticketLoading ? <ActivityIndicator color="#fff" /> : <Text style={s.confirmBtnTxt}>Generate Ticket</Text>}
                      </TouchableOpacity>

                      {ticketReceipt && (
                        <View style={s.ticketReceipt}>
                          <Text style={s.ticketReceiptTitle}>Metro Bus E-Ticket</Text>
                          <Text style={s.ticketReceiptLine}>Ticket ID: {ticketReceipt.ticket_id}</Text>
                          <Text style={s.ticketReceiptLine}>From: {ticketReceipt.from_stop}</Text>
                          <Text style={s.ticketReceiptLine}>To: {ticketReceipt.to_stop}</Text>
                          <Text style={s.ticketReceiptLine}>Distance: {ticketReceipt.distance_km} km</Text>
                          <Text style={s.ticketReceiptLine}>Fare: Rs {ticketReceipt.fare_rs.toFixed(2)}</Text>
                          <Text style={s.ticketReceiptLine}>Issued: {ticketReceipt.issued_at}</Text>
                          <View style={s.qrBox}>
                            <Text style={s.qrText}>{ticketReceipt.qr_code}</Text>
                          </View>
                          <Text style={s.qrCaption}>Simulated QR</Text>
                        </View>
                      )}
                    </View>
                  </View>
                )}

                {user && showTopup && (
                  <View>
                    <Text style={s.sectionLabel}>Select Amount</Text>
                    <View style={s.amountGrid}>
                      {TOPUP_AMOUNTS.map(amt => (
                        <TouchableOpacity
                          key={amt}
                          style={[s.amountChip, selectedAmount === amt && !customAmount && s.amountChipSelected]}
                          onPress={() => { setSelectedAmount(amt); setCustomAmount(''); }}>
                          <Text style={[s.amountChipTxt, selectedAmount === amt && !customAmount && s.amountChipTxtSelected]}>
                            Rs. {amt}
                          </Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                    <Text style={s.sectionLabel}>Or Enter Custom Amount</Text>
                    <TextInput
                      style={[s.customInput, customAmount ? s.customInputActive : null]}
                      placeholder="e.g. 350"
                      placeholderTextColor="#aaa"
                      keyboardType="numeric"
                      value={customAmount}
                      onChangeText={val => { setCustomAmount(val); setSelectedAmount(null); }}
                    />
                    <Text style={s.sectionLabel}>Select Payment Method</Text>
                    {PAYMENT_METHODS.map(method => (
                      <TouchableOpacity
                        key={method}
                        style={[s.methodRow, selectedMethod === method && s.methodRowSelected]}
                        onPress={() => setSelectedMethod(method)}>
                        <Text style={s.methodEmoji}>
                          {method === 'EasyPaisa' ? '📱' : method === 'JazzCash' ? '🎵' : method === 'NayaPay' ? '💚' : '🔵'}
                        </Text>
                        <Text style={[s.methodTxt, selectedMethod === method && s.methodTxtSelected]}>{method}</Text>
                        {selectedMethod === method && <Text style={s.checkmark}>✓</Text>}
                      </TouchableOpacity>
                    ))}
                    {finalAmount && finalAmount > 0 && selectedMethod && (
                      <View style={s.summaryBox}>
                        <Text style={s.summaryTxt}>Rs. {finalAmount} via {selectedMethod}</Text>
                      </View>
                    )}
                    <TouchableOpacity
                      style={[s.confirmBtn, (!finalAmount || !selectedMethod) && s.confirmBtnDisabled]}
                      onPress={handleTopup}
                      disabled={topupLoading || !finalAmount || !selectedMethod}>
                      {topupLoading ? <ActivityIndicator color="#fff" /> : <Text style={s.confirmBtnTxt}>Confirm Top Up</Text>}
                    </TouchableOpacity>
                  </View>
                )}
              </ScrollView>
            )}
          </View>
        </View>
      )}

      {/* AUTH MODAL */}
      <Modal visible={authScreen !== null} animationType="slide" onRequestClose={() => setAuthScreen(null)}>
        <View style={{flex: 1}}>
          {authScreen === 'login' && (
            <LoginScreen onLoginSuccess={handleLoginSuccess} onGoToSignup={() => setAuthScreen('signup')} onClose={() => setAuthScreen(null)} />
          )}
          {authScreen === 'signup' && (
            <SignupScreen onSignupSuccess={handleSignupSuccess} onGoToLogin={() => setAuthScreen('login')} onClose={() => setAuthScreen(null)} />
          )}
        </View>
      </Modal>
    </View>
  );
};

const s = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#000'},
  center: {flex: 1, justifyContent: 'center', alignItems: 'center'},
  loadTxt: {marginTop: 10, fontSize: 16, color: '#666'},

  topBar: {
    position: 'absolute', top: 0, left: 0, right: 0,
    backgroundColor: 'rgba(21, 101, 192, 0.95)',
    paddingHorizontal: 16, paddingTop: 44, paddingBottom: 12,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', zIndex: 10,
  },
  topTitle: {fontSize: 16, fontWeight: 'bold', color: '#fff'},
  refreshBtn: {width: 32, height: 32, borderRadius: 16, backgroundColor: 'rgba(255,255,255,0.2)', justifyContent: 'center', alignItems: 'center'},
  refreshTxt: {fontSize: 16},

  fabContainer: {position: 'absolute', right: 16, top: 120, gap: 12, zIndex: 10},
  fab: {width: 56, height: 56, borderRadius: 28, backgroundColor: '#1565C0', justifyContent: 'center', alignItems: 'center', elevation: 5},
  fabActive: {backgroundColor: '#0D47A1', transform: [{scale: 1.1}]},
  fabIcon: {fontSize: 24},

  // Bottom layer popup
  layersDock: {
    position: 'absolute',
    right: 16,
    bottom: 90,
    zIndex: 11,
    alignItems: 'flex-end',
  },
  layersPopup: {
    width: 250,
    backgroundColor: 'rgba(255,255,255,0.96)',
    borderRadius: 14,
    paddingVertical: 10,
    paddingHorizontal: 10,
    marginBottom: 8,
    elevation: 6,
  },
  layersTitle: {
    fontSize: 12,
    color: '#5f6368',
    fontWeight: '700',
    marginBottom: 8,
    textAlign: 'center',
  },
  layersRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 8,
  },
  layerChip: {
    borderWidth: 1,
    borderColor: '#d0d7de',
    backgroundColor: '#f8f9fa',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 7,
  },
  layerChipActive: {
    borderColor: '#1565C0',
    backgroundColor: '#E3F2FD',
  },
  layerChipText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#5f6368',
  },
  layerChipTextActive: {
    color: '#1565C0',
  },
  layersToggleBtn: {
    backgroundColor: 'rgba(21, 101, 192, 0.96)',
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 6,
  },
  layersToggleIcon: {
    color: '#fff',
    fontSize: 22,
    fontWeight: '700',
  },

  startJourneyDock: {
    position: 'absolute',
    left: 16,
    right: 16,
    bottom: 22,
    zIndex: 12,
    alignItems: 'center',
  },
  startJourneyBtn: {
    backgroundColor: '#2E7D32',
    borderRadius: 24,
    paddingHorizontal: 22,
    paddingVertical: 12,
    elevation: 8,
  },
  startJourneyBtnTxt: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '800',
  },
  stepsOverlay: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 13,
    paddingHorizontal: 12,
    paddingBottom: 14,
  },
  stepsPanel: {
    backgroundColor: 'rgba(255,255,255,0.98)',
    borderRadius: 14,
    padding: 12,
    elevation: 9,
  },
  stepsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  stepsHeaderActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  stepsStartBtn: {
    backgroundColor: '#E3F2FD',
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: '#1565C0',
  },
  stepsStartBtnTxt: {
    color: '#1565C0',
    fontSize: 11,
    fontWeight: '800',
  },
  stepsTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#1f2937',
  },
  stepsClose: {
    fontSize: 18,
    color: '#6b7280',
    fontWeight: '700',
  },
  stepRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  stepNo: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: '#1565C0',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
    marginTop: 1,
  },
  stepNoTxt: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '800',
  },
  stepTxt: {
    flex: 1,
    fontSize: 12,
    color: '#374151',
    lineHeight: 18,
  },

  modalOverlay: {position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.6)', zIndex: 20, justifyContent: 'flex-end'},
  modalContentInner: {backgroundColor: '#fff', borderTopLeftRadius: 20, borderTopRightRadius: 20, height: SCREEN_HEIGHT * 0.78, elevation: 10},
  modalHeader: {flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: '#eee'},
  modalHandle: {position: 'absolute', top: 8, left: '50%', marginLeft: -20, width: 40, height: 4, backgroundColor: '#ccc', borderRadius: 2},
  modalTitle: {flex: 1, fontSize: 17, fontWeight: 'bold', color: '#222', textAlign: 'center'},
  backBtn: {paddingHorizontal: 4},
  backTxt: {fontSize: 14, color: '#1565C0', fontWeight: '600'},
  closeBtn: {width: 32, height: 32, borderRadius: 16, backgroundColor: '#f0f0f0', justifyContent: 'center', alignItems: 'center'},
  closeTxt: {fontSize: 18, color: '#666'},
  modalBody: {flex: 1, padding: 16},

  // Stop selector
  searchBox: {padding: 12, borderBottomWidth: 1, borderBottomColor: '#eee'},
  searchInput: {backgroundColor: '#f5f5f5', borderRadius: 10, paddingHorizontal: 14, paddingVertical: 10, fontSize: 15, color: '#222'},
  stopItem: {flexDirection: 'row', alignItems: 'center', padding: 16},
  stopName: {fontSize: 15, color: '#222', fontWeight: '500'},
  stopRoutes: {fontSize: 12, color: '#888', marginTop: 2},
  stopArrow: {fontSize: 20, color: '#ccc', marginLeft: 8},

  // Journey planner
  journeySubtitle: {fontSize: 13, color: '#888', textAlign: 'center', marginBottom: 16},
  toggleRow: {flexDirection: 'row', gap: 10, marginBottom: 14},
  toggleBtn: {flex: 1, paddingVertical: 10, borderRadius: 12, backgroundColor: '#f1f3f5', borderWidth: 1, borderColor: '#e9ecef', alignItems: 'center'},
  toggleBtnActive: {backgroundColor: '#E3F2FD', borderColor: '#1565C0'},
  toggleTxt: {fontSize: 13, color: '#666', fontWeight: '700'},
  toggleTxtActive: {color: '#1565C0'},
  pointBtn: {borderWidth: 1, borderColor: '#ddd', borderRadius: 10, paddingHorizontal: 14, paddingVertical: 12, backgroundColor: '#fafafa', marginBottom: 8},
  pointBtnActive: {borderColor: '#1565C0', backgroundColor: '#E3F2FD'},
  pointBtnTxt: {fontSize: 13, color: '#333', fontWeight: '600'},
  hintTxt: {fontSize: 11, color: '#999', marginBottom: 10, textAlign: 'center'},
  inlineRow: {flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 8},
  chip: {paddingHorizontal: 12, paddingVertical: 8, borderRadius: 18, borderWidth: 1, borderColor: '#ddd', backgroundColor: '#fafafa'},
  chipActive: {backgroundColor: '#1565C0', borderColor: '#1565C0'},
  chipTxt: {fontSize: 12, color: '#666', fontWeight: '700'},
  chipTxtActive: {color: '#fff'},
  label: {fontSize: 13, fontWeight: '600', color: '#444', marginBottom: 6, marginTop: 4},
  stopSelector: {
    borderWidth: 1, borderColor: '#ddd', borderRadius: 10,
    paddingHorizontal: 14, paddingVertical: 14,
    backgroundColor: '#fafafa', flexDirection: 'row', alignItems: 'center', marginBottom: 8,
  },
  stopSelectorFilled: {borderColor: '#1565C0', backgroundColor: '#E3F2FD'},
  stopSelectorTxt: {flex: 1, fontSize: 14, color: '#1565C0', fontWeight: '500'},
  stopSelectorPlaceholder: {flex: 1, fontSize: 14, color: '#aaa'},
  dropdownArrow: {fontSize: 12, color: '#aaa'},
  swapBtn: {alignSelf: 'center', backgroundColor: '#E3F2FD', paddingHorizontal: 16, paddingVertical: 6, borderRadius: 20, marginBottom: 8},
  swapTxt: {fontSize: 13, color: '#1565C0', fontWeight: '600'},
  planBtn: {backgroundColor: '#1565C0', borderRadius: 25, paddingVertical: 14, alignItems: 'center', marginTop: 8, elevation: 3},
  planBtnDisabled: {backgroundColor: '#90CAF9'},
  planBtnTxt: {color: '#fff', fontSize: 16, fontWeight: 'bold'},

  errorBox: {alignItems: 'center', paddingVertical: 24, marginTop: 12},
  errorEmoji: {fontSize: 36, marginBottom: 8},
  errorTxt: {fontSize: 14, color: '#888', textAlign: 'center', marginBottom: 4},
  errorHint: {fontSize: 12, color: '#bbb'},

  resultsContainer: {marginTop: 16},
  resultsTitle: {fontSize: 16, fontWeight: 'bold', color: '#2E7D32', marginBottom: 4},
  resultsSubtitle: {fontSize: 12, color: '#888', marginBottom: 12},
  resultCard: {
    backgroundColor: '#fff', borderRadius: 12, padding: 16,
    marginBottom: 12, borderWidth: 1, borderColor: '#eee', elevation: 2,
  },
  resultCardBest: {borderColor: '#1565C0', borderWidth: 2},
  bestBadge: {
    alignSelf: 'flex-start', backgroundColor: '#1565C0',
    borderRadius: 8, paddingHorizontal: 8, paddingVertical: 3, marginBottom: 8,
  },
  bestBadgeTxt: {color: '#fff', fontSize: 11, fontWeight: 'bold'},
  resultRouteName: {fontSize: 15, fontWeight: 'bold', color: '#222', marginBottom: 8},
  routePathRow: {flexDirection: 'row', alignItems: 'center', marginBottom: 10},
  routeFrom: {flex: 1, fontSize: 13, color: '#1565C0', fontWeight: '500'},
  routeArrow: {fontSize: 13, color: '#aaa'},
  routeTo: {flex: 1, fontSize: 13, color: '#E53935', fontWeight: '500', textAlign: 'right'},
  statsRow: {flexDirection: 'row', justifyContent: 'space-around', marginBottom: 8},
  statChip: {alignItems: 'center', backgroundColor: '#F5F5F5', borderRadius: 8, padding: 8, flex: 1, marginHorizontal: 3},
  statEmoji: {fontSize: 16, marginBottom: 2},
  statVal: {fontSize: 12, fontWeight: 'bold', color: '#1565C0'},
  statLbl: {fontSize: 10, color: '#888'},
  segmentsBox: {marginTop: 8, backgroundColor: '#F9F9F9', borderRadius: 8, padding: 10},
  segRow: {flexDirection: 'row', alignItems: 'flex-start', marginBottom: 6},
  segDot: {width: 8, height: 8, borderRadius: 4, backgroundColor: '#1565C0', marginTop: 5, marginRight: 8},
  segTxt: {flex: 1, fontSize: 12, color: '#555'},
  actionsRow: {flexDirection: 'row', justifyContent: 'flex-end', marginTop: 8},
  selectBtn: {backgroundColor: '#0D47A1', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 10},
  selectBtnTxt: {color: '#fff', fontSize: 12, fontWeight: '800'},

  // Bus list
  busCountBox: {backgroundColor: '#1565C0', padding: 12, borderRadius: 8, marginBottom: 12},
  busCountTxt: {fontSize: 18, fontWeight: 'bold', color: '#fff', textAlign: 'center'},
  busUpdateTxt: {fontSize: 12, color: '#E3F2FD', textAlign: 'center', marginTop: 4},
  emptyState: {alignItems: 'center', paddingVertical: 48},
  emptyText: {fontSize: 18, fontWeight: 'bold', color: '#999', marginBottom: 8},
  emptySubtext: {fontSize: 14, color: '#bbb', textAlign: 'center'},
  card: {backgroundColor: '#fff', marginBottom: 12, padding: 14, borderRadius: 10, elevation: 2, borderWidth: 1, borderColor: '#eee'},
  cardHead: {flexDirection: 'row', alignItems: 'center', marginBottom: 8},
  cardId: {fontSize: 15, fontWeight: 'bold', color: '#000', flex: 1},
  badge: {paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8},
  fBadge: {backgroundColor: '#E8F5E9'},
  rBadge: {backgroundColor: '#FBE9E7'},
  badgeTxt: {fontSize: 11, fontWeight: 'bold', color: '#333'},
  cardRoute: {fontSize: 13, color: '#2196F3', marginBottom: 4},
  cardSpeed: {fontSize: 13, color: '#FF9800', marginBottom: 4},
  cardCoord: {fontSize: 11, color: '#999'},

  // E-Ticket
  eticketContainer: {alignItems: 'center', paddingVertical: 16},
  eticketTitle: {fontSize: 18, fontWeight: 'bold', color: '#222', marginBottom: 24, textAlign: 'center'},
  eticketBtn: {backgroundColor: '#1565C0', paddingHorizontal: 32, paddingVertical: 16, borderRadius: 25, elevation: 3, marginBottom: 16},
  eticketBtnTxt: {color: '#fff', fontSize: 16, fontWeight: 'bold'},
  eticketInfo: {fontSize: 14, color: '#4CAF50', textAlign: 'center', marginBottom: 16},
  infoBox: {backgroundColor: '#E3F2FD', padding: 16, borderRadius: 8, width: '100%'},
  infoText: {fontSize: 13, color: '#1565C0', marginBottom: 4},
  seniorBanner: {backgroundColor: '#E8F5E9', borderRadius: 8, padding: 12, marginBottom: 12, borderLeftWidth: 4, borderLeftColor: '#4CAF50'},
  seniorBannerTxt: {color: '#2E7D32', fontSize: 14, fontWeight: 'bold', textAlign: 'center'},
  walletCard: {backgroundColor: '#1565C0', borderRadius: 16, padding: 24, alignItems: 'center', marginBottom: 16},
  walletGreeting: {fontSize: 16, color: '#E3F2FD', marginBottom: 8},
  walletLabel: {fontSize: 13, color: '#90CAF9', marginBottom: 4},
  walletBalance: {fontSize: 36, fontWeight: 'bold', color: '#fff'},
  topupBtn: {backgroundColor: '#4CAF50', borderRadius: 25, paddingVertical: 14, alignItems: 'center', marginBottom: 12, elevation: 2},
  topupBtnTxt: {color: '#fff', fontSize: 15, fontWeight: 'bold'},
  logoutBtn: {borderWidth: 1, borderColor: '#ddd', borderRadius: 25, paddingVertical: 12, alignItems: 'center'},
  logoutBtnTxt: {color: '#888', fontSize: 14},
  sectionLabel: {fontSize: 14, fontWeight: '700', color: '#444', marginBottom: 10, marginTop: 4},
  amountGrid: {flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 20},
  amountChip: {borderWidth: 2, borderColor: '#ddd', borderRadius: 10, paddingHorizontal: 18, paddingVertical: 10, backgroundColor: '#fafafa'},
  amountChipSelected: {borderColor: '#1565C0', backgroundColor: '#E3F2FD'},
  amountChipTxt: {fontSize: 14, color: '#666', fontWeight: '600'},
  amountChipTxtSelected: {color: '#1565C0'},
  customInput: {borderWidth: 1, borderColor: '#ddd', borderRadius: 10, paddingHorizontal: 14, paddingVertical: 12, fontSize: 15, color: '#222', backgroundColor: '#fafafa', marginBottom: 20},
  customInputActive: {borderColor: '#1565C0', backgroundColor: '#E3F2FD'},
  methodRow: {flexDirection: 'row', alignItems: 'center', borderWidth: 1, borderColor: '#eee', borderRadius: 10, padding: 14, marginBottom: 8, backgroundColor: '#fafafa'},
  methodRowSelected: {borderColor: '#1565C0', backgroundColor: '#E3F2FD'},
  methodEmoji: {fontSize: 20, marginRight: 12},
  methodTxt: {flex: 1, fontSize: 15, color: '#444'},
  methodTxtSelected: {color: '#1565C0', fontWeight: '600'},
  checkmark: {fontSize: 18, color: '#1565C0', fontWeight: 'bold'},
  summaryBox: {backgroundColor: '#E8F5E9', borderRadius: 8, padding: 12, marginVertical: 12, alignItems: 'center'},
  summaryTxt: {color: '#2E7D32', fontSize: 14, fontWeight: '600'},
  confirmBtn: {backgroundColor: '#1565C0', borderRadius: 25, paddingVertical: 15, alignItems: 'center', elevation: 3},
  confirmBtnDisabled: {backgroundColor: '#90CAF9'},
  confirmBtnTxt: {color: '#fff', fontSize: 16, fontWeight: 'bold'},

  ticketSection: {
    marginTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    paddingTop: 14,
  },
  ticketSectionTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 8,
  },
  ticketFarePreview: {
    marginTop: 6,
    marginBottom: 10,
    fontSize: 12,
    color: '#374151',
    fontWeight: '600',
  },
  ticketReceipt: {
    marginTop: 14,
    backgroundColor: '#ffffff',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    padding: 12,
  },
  ticketReceiptTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 8,
    textAlign: 'center',
  },
  ticketReceiptLine: {
    fontSize: 12,
    color: '#111827',
    marginBottom: 3,
  },
  qrBox: {
    marginTop: 10,
    padding: 8,
    borderWidth: 1,
    borderColor: '#111827',
    borderRadius: 8,
    backgroundColor: '#fff',
    alignItems: 'center',
  },
  qrText: {
    fontFamily: 'monospace',
    fontSize: 8,
    lineHeight: 8,
    color: '#111827',
  },
  qrCaption: {
    marginTop: 6,
    fontSize: 11,
    color: '#6b7280',
    textAlign: 'center',
    fontWeight: '600',
  },
});

export default MapScreen;
