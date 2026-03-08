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

const {height: SCREEN_HEIGHT} = Dimensions.get('window');
const API_URL = 'http://10.0.2.2:8000';

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

interface JourneyOption {
  route_id?: string;
  route_name?: string;
  total_distance?: number;
  estimated_time?: number;
  estimated_fare?: number;
  segments?: any[];
  transfers?: number;
  confidence?: number;
}

const TOPUP_AMOUNTS = [100, 200, 500, 1000];
const PAYMENT_METHODS = ['EasyPaisa', 'JazzCash', 'NayaPay', 'SadaPay'];

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
      const r = await fetch(`${API_URL}/api/journey/transfer-points`);
      const data = await r.json();
      if (data.success && data.transfer_points) {
        // Clean up stop names - remove "Transfer Hub near " prefix
        const cleaned = data.transfer_points.map((s: any) => ({
          ...s,
          name: s.name.replace('Transfer Hub near ', ''),
        }));
        // Deduplicate by name
        const seen = new Set();
        const unique = cleaned.filter((s: Stop) => {
          if (seen.has(s.name)) return false;
          seen.add(s.name);
          return true;
        });
        setStops(unique);
      }
    } catch (e) {
      console.error('Failed to fetch stops:', e);
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
    setActiveModal(type);
    if (type === 'journey' && stops.length === 0) {
      fetchStops();
    }
  };

  const closeModal = () => {
    setShowTopup(false);
    setSelectingStop(null);
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
    if (!fromStop || !toStop) {
      Alert.alert('Error', 'Please select both From and To stops');
      return;
    }
    if (fromStop.id === toStop.id) {
      Alert.alert('Error', 'From and To stops cannot be the same');
      return;
    }
    setJourneyLoading(true);
    setJourneyResults(null);
    setJourneyError('');
    try {
      const res = await fetch(`${API_URL}/api/journey/plan`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          origin_lat: fromStop.location[0],
          origin_lng: fromStop.location[1],
          destination_lat: toStop.location[0],
          destination_lng: toStop.location[1],
          preferences: {
            optimize_for: 'time',
            max_transfers: 3,
          },
        }),
      });
      const data = await res.json();

      if (data.success === false || data.detail) {
        setJourneyError(data.message || data.detail || 'No route found');
      } else {
        // Handle different response shapes
        const options = data.journey_options || data.options || (data.route ? [data] : null);
        if (options && options.length > 0) {
          setJourneyResults(options);
        } else if (data.route_id || data.segments) {
          setJourneyResults([data]);
        } else {
          setJourneyError('No routes found between these stops');
        }
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
  const currentSearch = selectingStop === 'from' ? fromSearch : toSearch;

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

      {/* Bottom Sheet Modal */}
      {activeModal !== null && (
        <View style={s.modalOverlay}>
          <TouchableOpacity style={{flex: 1}} activeOpacity={1} onPress={closeModal} />
          <View style={s.modalContentInner}>
            <View style={s.modalHeader}>
              <View style={s.modalHandle} />
              {(showTopup || selectingStop) ? (
                <TouchableOpacity style={s.backBtn} onPress={() => { setShowTopup(false); setSelectingStop(null); }}>
                  <Text style={s.backTxt}>← Back</Text>
                </TouchableOpacity>
              ) : (
                <View style={{width: 60}} />
              )}
              <Text style={s.modalTitle}>
                {activeModal === 'list' ? '📋 Bus List' :
                 activeModal === 'journey' ? (selectingStop ? `Select ${selectingStop === 'from' ? 'From' : 'To'} Stop` : '🗺️ Journey Planner') :
                 showTopup ? '💳 Top Up' : '🎫 E-Ticket'}
              </Text>
              <TouchableOpacity style={s.closeBtn} onPress={closeModal}>
                <Text style={s.closeTxt}>✕</Text>
              </TouchableOpacity>
            </View>

            {/* STOP SELECTOR */}
            {activeModal === 'journey' && selectingStop && (
              <View style={{flex: 1}}>
                <View style={s.searchBox}>
                  <TextInput
                    style={s.searchInput}
                    placeholder={`Search ${selectingStop === 'from' ? 'departure' : 'destination'} stop...`}
                    placeholderTextColor="#aaa"
                    value={currentSearch}
                    onChangeText={val => selectingStop === 'from' ? setFromSearch(val) : setToSearch(val)}
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
                      <TouchableOpacity style={s.stopItem} onPress={() => selectStop(item)}>
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
            )}

            {/* JOURNEY PLANNER MAIN */}
            {activeModal === 'journey' && !selectingStop && (
              <ScrollView style={s.modalBody} contentContainerStyle={{paddingBottom: 20}}>
                <Text style={s.journeySubtitle}>Find the best route between stops</Text>

                {/* FROM */}
                <Text style={s.label}>📍 From</Text>
                <TouchableOpacity
                  style={[s.stopSelector, fromStop && s.stopSelectorFilled]}
                  onPress={() => { setSelectingStop('from'); setFromSearch(fromStop?.name || ''); }}>
                  <Text style={fromStop ? s.stopSelectorTxt : s.stopSelectorPlaceholder}>
                    {fromStop ? fromStop.name : 'Tap to select departure stop'}
                  </Text>
                  <Text style={s.dropdownArrow}>▼</Text>
                </TouchableOpacity>

                {/* SWAP */}
                <TouchableOpacity style={s.swapBtn} onPress={swapStops}>
                  <Text style={s.swapTxt}>⇅ Swap</Text>
                </TouchableOpacity>

                {/* TO */}
                <Text style={s.label}>🏁 To</Text>
                <TouchableOpacity
                  style={[s.stopSelector, toStop && s.stopSelectorFilled]}
                  onPress={() => { setSelectingStop('to'); setToSearch(toStop?.name || ''); }}>
                  <Text style={toStop ? s.stopSelectorTxt : s.stopSelectorPlaceholder}>
                    {toStop ? toStop.name : 'Tap to select destination stop'}
                  </Text>
                  <Text style={s.dropdownArrow}>▼</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[s.planBtn, (!fromStop || !toStop || journeyLoading) && s.planBtnDisabled]}
                  onPress={handlePlanJourney}
                  disabled={!fromStop || !toStop || journeyLoading}>
                  {journeyLoading ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={s.planBtnTxt}>🔍 Plan Journey</Text>
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
                    <Text style={s.resultsSubtitle}>Sorted by best option (time + fare)</Text>

                    {journeyResults.map((option, i) => (
                      <View key={i} style={[s.resultCard, i === 0 && s.resultCardBest]}>
                        {i === 0 && (
                          <View style={s.bestBadge}>
                            <Text style={s.bestBadgeTxt}>⭐ BEST</Text>
                          </View>
                        )}

                        {/* Route name */}
                        <Text style={s.resultRouteName}>
                          🚌 {option.route_name || option.route_id || `Option ${i + 1}`}
                        </Text>

                        {/* From → To */}
                        <View style={s.routePathRow}>
                          <Text style={s.routeFrom} numberOfLines={1}>{fromStop?.name}</Text>
                          <Text style={s.routeArrow}> → </Text>
                          <Text style={s.routeTo} numberOfLines={1}>{toStop?.name}</Text>
                        </View>

                        {/* Stats */}
                        <View style={s.statsRow}>
                          {option.total_distance != null && (
                            <View style={s.statChip}>
                              <Text style={s.statEmoji}>📏</Text>
                              <Text style={s.statVal}>{Number(option.total_distance).toFixed(1)} km</Text>
                              <Text style={s.statLbl}>Distance</Text>
                            </View>
                          )}
                          {option.estimated_time != null && (
                            <View style={s.statChip}>
                              <Text style={s.statEmoji}>⏱️</Text>
                              <Text style={s.statVal}>{Math.round(option.estimated_time)} min</Text>
                              <Text style={s.statLbl}>Est. Time</Text>
                            </View>
                          )}
                          {option.estimated_fare != null && (
                            <View style={s.statChip}>
                              <Text style={s.statEmoji}>💰</Text>
                              <Text style={s.statVal}>Rs. {option.estimated_fare}</Text>
                              <Text style={s.statLbl}>Fare</Text>
                            </View>
                          )}
                          {option.transfers != null && (
                            <View style={s.statChip}>
                              <Text style={s.statEmoji}>🔄</Text>
                              <Text style={s.statVal}>{option.transfers}</Text>
                              <Text style={s.statLbl}>Transfers</Text>
                            </View>
                          )}
                        </View>

                        {/* Segments */}
                        {option.segments && option.segments.length > 0 && (
                          <View style={s.segmentsBox}>
                            {option.segments.map((seg: any, j: number) => (
                              <View key={j} style={s.segRow}>
                                <View style={s.segDot} />
                                <Text style={s.segTxt}>
                                  {seg.instruction || seg.description || seg.route_id || JSON.stringify(seg)}
                                </Text>
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
                      <Text style={s.infoText}>💰 Fare: Rs. 10/km (Min Rs. 20)</Text>
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
});

export default MapScreen;
