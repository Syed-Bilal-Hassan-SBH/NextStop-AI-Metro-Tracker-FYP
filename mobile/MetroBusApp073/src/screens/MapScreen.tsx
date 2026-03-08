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

const TOPUP_AMOUNTS = [100, 200, 500, 1000];
const PAYMENT_METHODS = ['EasyPaisa', 'JazzCash', 'NayaPay', 'SadaPay'];

const MapScreen = () => {
  const [buses, setBuses] = useState<Bus[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState('');
  const [activeModal, setActiveModal] = useState<'list' | 'eticket' | null>(null);
  const [authScreen, setAuthScreen] = useState<'login' | 'signup' | null>(null);
  const [user, setUser] = useState<User | null>(null);

  // Top-up state
  const [showTopup, setShowTopup] = useState(false);
  const [selectedAmount, setSelectedAmount] = useState<number | null>(null);
  const [customAmount, setCustomAmount] = useState('');
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null);
  const [topupLoading, setTopupLoading] = useState(false);

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

  useEffect(() => {
    fetchBuses();
    const iv = setInterval(fetchBuses, 5000);
    return () => clearInterval(iv);
  }, []);

  const openModal = (type: 'list' | 'eticket') => {
    setShowTopup(false);
    setActiveModal(type);
  };

  const closeModal = () => {
    setShowTopup(false);
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
        body: JSON.stringify({
          email: user?.email,
          amount: finalAmount,
          method: selectedMethod,
        }),
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

  const hideWebUI = () => {
    const jsCode = `
      (function() {
        setTimeout(function() {
          var elementsToHide = [
            '.header', '.department-info', '.stats-container',
            '.control-panel', '.eticket-button',
            'button:not(.leaflet-control button)',
          ];
          elementsToHide.forEach(function(selector) {
            var elements = document.querySelectorAll(selector);
            elements.forEach(function(el) {
              if (!el.classList.contains('leaflet-control') && 
                  !el.closest('.leaflet-control') && el.id !== 'map') {
                el.style.display = 'none';
              }
            });
          });
          var allDivs = document.querySelectorAll('div');
          allDivs.forEach(function(div) {
            var style = window.getComputedStyle(div);
            if (style.position === 'absolute' && div.id !== 'map' && 
                !div.classList.contains('leaflet-control') &&
                !div.closest('.leaflet-control') && !div.closest('#map')) {
              div.style.display = 'none';
            }
          });
          var mapEl = document.getElementById('map');
          if (mapEl) {
            mapEl.style.position = 'fixed';
            mapEl.style.top = '0'; mapEl.style.left = '0';
            mapEl.style.width = '100vw'; mapEl.style.height = '100vh';
            mapEl.style.zIndex = '1';
          }
          document.body.style.margin = '0';
          document.body.style.padding = '0';
          document.body.style.overflow = 'hidden';
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
            webviewRef.current?.injectJavaScript(`
              if (window.map && window.map.invalidateSize) window.map.invalidateSize();
              true;
            `);
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
        <TouchableOpacity
          style={[s.fab, activeModal === 'list' && s.fabActive]}
          onPress={() => openModal('list')}>
          <Text style={s.fabIcon}>📋</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[s.fab, activeModal === 'eticket' && s.fabActive]}
          onPress={() => openModal('eticket')}>
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
              {showTopup ? (
                <TouchableOpacity style={s.backBtn} onPress={() => setShowTopup(false)}>
                  <Text style={s.backTxt}>← Back</Text>
                </TouchableOpacity>
              ) : (
                <View style={{width: 60}} />
              )}
              <Text style={s.modalTitle}>
                {activeModal === 'list' ? '📋 Bus List' : showTopup ? '💳 Top Up' : '🎫 E-Ticket'}
              </Text>
              <TouchableOpacity style={s.closeBtn} onPress={closeModal}>
                <Text style={s.closeTxt}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={s.modalBody} contentContainerStyle={{paddingBottom: 20}}>

              {/* BUS LIST */}
              {activeModal === 'list' && (
                <View>
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
                            <Text style={s.badgeTxt}>
                              {bus.bus_id?.includes('-F-') ? '▶ FWD' : '◀ REV'}
                            </Text>
                          </View>
                        </View>
                        <Text style={s.cardRoute}>Route: {bus.route_id}</Text>
                        {bus.speed != null && (
                          <Text style={s.cardSpeed}>⚡ {Number(bus.speed).toFixed(1)} km/h</Text>
                        )}
                        <Text style={s.cardCoord}>
                          📍 {bus.current_lat?.toFixed(4)}, {bus.current_lng?.toFixed(4)}
                        </Text>
                      </View>
                    ))
                  )}
                </View>
              )}

              {/* E-TICKET - NOT LOGGED IN */}
              {activeModal === 'eticket' && !user && (
                <View style={s.eticketContainer}>
                  <Text style={s.eticketTitle}>Purchase Metro Bus E-Ticket</Text>
                  <TouchableOpacity
                    style={s.eticketBtn}
                    onPress={() => setAuthScreen('login')}>
                    <Text style={s.eticketBtnTxt}>Login / Sign Up</Text>
                  </TouchableOpacity>
                  <Text style={s.eticketInfo}>🎉 Senior citizens (60+) travel FREE!</Text>
                  <View style={s.infoBox}>
                    <Text style={s.infoText}>💳 Top-up: EasyPaisa, JazzCash, NayaPay, SadaPay</Text>
                    <Text style={s.infoText}>💰 Fare: Rs. 10/km (Min Rs. 20)</Text>
                  </View>
                </View>
              )}

              {/* E-TICKET - LOGGED IN - WALLET VIEW */}
              {activeModal === 'eticket' && user && !showTopup && (
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
                  <TouchableOpacity
                    style={s.topupBtn}
                    onPress={() => setShowTopup(true)}>
                    <Text style={s.topupBtnTxt}>💳 Top Up Wallet</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={s.logoutBtn} onPress={handleLogout}>
                    <Text style={s.logoutBtnTxt}>Logout</Text>
                  </TouchableOpacity>
                </View>
              )}

              {/* TOP-UP VIEW */}
              {activeModal === 'eticket' && user && showTopup && (
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
                    onChangeText={val => {
                      setCustomAmount(val);
                      setSelectedAmount(null);
                    }}
                  />

                  <Text style={s.sectionLabel}>Select Payment Method</Text>
                  {PAYMENT_METHODS.map(method => (
                    <TouchableOpacity
                      key={method}
                      style={[s.methodRow, selectedMethod === method && s.methodRowSelected]}
                      onPress={() => setSelectedMethod(method)}>
                      <Text style={s.methodEmoji}>
                        {method === 'EasyPaisa' ? '📱' :
                         method === 'JazzCash' ? '🎵' :
                         method === 'NayaPay' ? '💚' : '🔵'}
                      </Text>
                      <Text style={[s.methodTxt, selectedMethod === method && s.methodTxtSelected]}>
                        {method}
                      </Text>
                      {selectedMethod === method && <Text style={s.checkmark}>✓</Text>}
                    </TouchableOpacity>
                  ))}

                  {finalAmount && finalAmount > 0 && selectedMethod && (
                    <View style={s.summaryBox}>
                      <Text style={s.summaryTxt}>
                        Rs. {finalAmount} via {selectedMethod}
                      </Text>
                    </View>
                  )}

                  <TouchableOpacity
                    style={[s.confirmBtn, (!finalAmount || !selectedMethod) && s.confirmBtnDisabled]}
                    onPress={handleTopup}
                    disabled={topupLoading || !finalAmount || !selectedMethod}>
                    {topupLoading ? (
                      <ActivityIndicator color="#fff" />
                    ) : (
                      <Text style={s.confirmBtnTxt}>Confirm Top Up</Text>
                    )}
                  </TouchableOpacity>
                </View>
              )}

            </ScrollView>
          </View>
        </View>
      )}

      {/* AUTH MODAL */}
      <Modal
        visible={authScreen !== null}
        animationType="slide"
        onRequestClose={() => setAuthScreen(null)}>
        <View style={{flex: 1}}>
          {authScreen === 'login' && (
            <LoginScreen
              onLoginSuccess={handleLoginSuccess}
              onGoToSignup={() => setAuthScreen('signup')}
              onClose={() => setAuthScreen(null)}
            />
          )}
          {authScreen === 'signup' && (
            <SignupScreen
              onSignupSuccess={handleSignupSuccess}
              onGoToLogin={() => setAuthScreen('login')}
              onClose={() => setAuthScreen(null)}
            />
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
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    zIndex: 10,
  },
  topTitle: {fontSize: 16, fontWeight: 'bold', color: '#fff'},
  refreshBtn: {
    width: 32, height: 32, borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center', alignItems: 'center',
  },
  refreshTxt: {fontSize: 16},

  fabContainer: {position: 'absolute', right: 16, top: 120, gap: 12, zIndex: 10},
  fab: {
    width: 56, height: 56, borderRadius: 28, backgroundColor: '#1565C0',
    justifyContent: 'center', alignItems: 'center', elevation: 5,
  },
  fabActive: {backgroundColor: '#0D47A1', transform: [{scale: 1.1}]},
  fabIcon: {fontSize: 24},

  modalOverlay: {
    position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.6)', zIndex: 20, justifyContent: 'flex-end',
  },
  modalContentInner: {
    backgroundColor: '#fff', borderTopLeftRadius: 20, borderTopRightRadius: 20,
    height: SCREEN_HEIGHT * 0.7, elevation: 10,
  },
  modalHeader: {
    flexDirection: 'row', alignItems: 'center',
    padding: 16, borderBottomWidth: 1, borderBottomColor: '#eee',
  },
  modalHandle: {
    position: 'absolute', top: 8, left: '50%', marginLeft: -20,
    width: 40, height: 4, backgroundColor: '#ccc', borderRadius: 2,
  },
  modalTitle: {flex: 1, fontSize: 18, fontWeight: 'bold', color: '#222', textAlign: 'center'},
  backBtn: {paddingHorizontal: 4},
  backTxt: {fontSize: 14, color: '#1565C0', fontWeight: '600'},
  closeBtn: {
    width: 32, height: 32, borderRadius: 16,
    backgroundColor: '#f0f0f0', justifyContent: 'center', alignItems: 'center',
  },
  closeTxt: {fontSize: 18, color: '#666'},
  modalBody: {flex: 1, padding: 16},

  busCountBox: {backgroundColor: '#1565C0', padding: 12, borderRadius: 8, marginBottom: 12},
  busCountTxt: {fontSize: 18, fontWeight: 'bold', color: '#fff', textAlign: 'center'},
  busUpdateTxt: {fontSize: 12, color: '#E3F2FD', textAlign: 'center', marginTop: 4},

  emptyState: {alignItems: 'center', paddingVertical: 48},
  emptyText: {fontSize: 18, fontWeight: 'bold', color: '#999', marginBottom: 8},
  emptySubtext: {fontSize: 14, color: '#bbb', textAlign: 'center'},

  card: {
    backgroundColor: '#fff', marginBottom: 12, padding: 14,
    borderRadius: 10, elevation: 2, borderWidth: 1, borderColor: '#eee',
  },
  cardHead: {flexDirection: 'row', alignItems: 'center', marginBottom: 8},
  cardId: {fontSize: 15, fontWeight: 'bold', color: '#000', flex: 1},
  badge: {paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8},
  fBadge: {backgroundColor: '#E8F5E9'},
  rBadge: {backgroundColor: '#FBE9E7'},
  badgeTxt: {fontSize: 11, fontWeight: 'bold', color: '#333'},
  cardRoute: {fontSize: 13, color: '#2196F3', marginBottom: 4},
  cardSpeed: {fontSize: 13, color: '#FF9800', marginBottom: 4},
  cardCoord: {fontSize: 11, color: '#999'},

  eticketContainer: {alignItems: 'center', paddingVertical: 16},
  eticketTitle: {fontSize: 18, fontWeight: 'bold', color: '#222', marginBottom: 24, textAlign: 'center'},
  eticketBtn: {
    backgroundColor: '#1565C0', paddingHorizontal: 32, paddingVertical: 16,
    borderRadius: 25, elevation: 3, marginBottom: 16,
  },
  eticketBtnTxt: {color: '#fff', fontSize: 16, fontWeight: 'bold'},
  eticketInfo: {fontSize: 14, color: '#4CAF50', textAlign: 'center', marginBottom: 16},
  infoBox: {backgroundColor: '#E3F2FD', padding: 16, borderRadius: 8, width: '100%'},
  infoText: {fontSize: 13, color: '#1565C0', marginBottom: 4},

  seniorBanner: {
    backgroundColor: '#E8F5E9', borderRadius: 8, padding: 12,
    marginBottom: 12, borderLeftWidth: 4, borderLeftColor: '#4CAF50',
  },
  seniorBannerTxt: {color: '#2E7D32', fontSize: 14, fontWeight: 'bold', textAlign: 'center'},

  walletCard: {
    backgroundColor: '#1565C0', borderRadius: 16, padding: 24,
    alignItems: 'center', marginBottom: 16,
  },
  walletGreeting: {fontSize: 16, color: '#E3F2FD', marginBottom: 8},
  walletLabel: {fontSize: 13, color: '#90CAF9', marginBottom: 4},
  walletBalance: {fontSize: 36, fontWeight: 'bold', color: '#fff'},

  topupBtn: {
    backgroundColor: '#4CAF50', borderRadius: 25, paddingVertical: 14,
    alignItems: 'center', marginBottom: 12, elevation: 2,
  },
  topupBtnTxt: {color: '#fff', fontSize: 15, fontWeight: 'bold'},

  logoutBtn: {
    borderWidth: 1, borderColor: '#ddd', borderRadius: 25,
    paddingVertical: 12, alignItems: 'center',
  },
  logoutBtnTxt: {color: '#888', fontSize: 14},

  sectionLabel: {fontSize: 14, fontWeight: '700', color: '#444', marginBottom: 10, marginTop: 4},
  amountGrid: {flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 20},
  amountChip: {
    borderWidth: 2, borderColor: '#ddd', borderRadius: 10,
    paddingHorizontal: 18, paddingVertical: 10, backgroundColor: '#fafafa',
  },
  amountChipSelected: {borderColor: '#1565C0', backgroundColor: '#E3F2FD'},
  amountChipTxt: {fontSize: 14, color: '#666', fontWeight: '600'},
  amountChipTxtSelected: {color: '#1565C0'},

  customInput: {
    borderWidth: 1, borderColor: '#ddd', borderRadius: 10,
    paddingHorizontal: 14, paddingVertical: 12,
    fontSize: 15, color: '#222', backgroundColor: '#fafafa',
    marginBottom: 20,
  },
  customInputActive: {
    borderColor: '#1565C0', backgroundColor: '#E3F2FD',
  },

  methodRow: {
    flexDirection: 'row', alignItems: 'center',
    borderWidth: 1, borderColor: '#eee', borderRadius: 10,
    padding: 14, marginBottom: 8, backgroundColor: '#fafafa',
  },
  methodRowSelected: {borderColor: '#1565C0', backgroundColor: '#E3F2FD'},
  methodEmoji: {fontSize: 20, marginRight: 12},
  methodTxt: {flex: 1, fontSize: 15, color: '#444'},
  methodTxtSelected: {color: '#1565C0', fontWeight: '600'},
  checkmark: {fontSize: 18, color: '#1565C0', fontWeight: 'bold'},

  summaryBox: {
    backgroundColor: '#E8F5E9', borderRadius: 8, padding: 12,
    marginVertical: 12, alignItems: 'center',
  },
  summaryTxt: {color: '#2E7D32', fontSize: 14, fontWeight: '600'},

  confirmBtn: {
    backgroundColor: '#1565C0', borderRadius: 25, paddingVertical: 15,
    alignItems: 'center', elevation: 3,
  },
  confirmBtnDisabled: {backgroundColor: '#90CAF9'},
  confirmBtnTxt: {color: '#fff', fontSize: 16, fontWeight: 'bold'},
});

export default MapScreen;
