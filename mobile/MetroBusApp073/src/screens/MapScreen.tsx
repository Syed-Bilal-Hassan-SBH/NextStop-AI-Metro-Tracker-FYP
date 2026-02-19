import React, {useEffect, useState, useRef} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Dimensions,
  ScrollView,
  Animated,
} from 'react-native';
import WebView from 'react-native-webview';

const {height: SCREEN_HEIGHT, width: SCREEN_WIDTH} = Dimensions.get('window');

interface Bus {
  bus_id: string;
  current_lat: number;
  current_lng: number;
  status: string;
  route_id: string;
  speed?: number;
}

const MapScreen = () => {
  const [buses, setBuses] = useState<Bus[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState('');
  const [activeModal, setActiveModal] = useState<'list' | 'eticket' | null>(null);
  const webviewRef = useRef<any>(null);
  const slideAnim = useRef(new Animated.Value(SCREEN_HEIGHT)).current;

  const fetchBuses = async () => {
    try {
      const r = await fetch('http://10.0.2.2:8000/api/buses');
      const data = await r.json();
      const arr = Array.isArray(data) ? data : data.buses || [];
      setBuses(arr);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBuses();
    const iv = setInterval(fetchBuses, 5000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    if (activeModal !== null) {
      Animated.spring(slideAnim, {
        toValue: 0,
        useNativeDriver: true,
        tension: 50,
        friction: 8,
      }).start();
    } else {
      Animated.timing(slideAnim, {
        toValue: SCREEN_HEIGHT,
        duration: 300,
        useNativeDriver: true,
      }).start();
    }
  }, [activeModal]);

  const openModal = (type: 'list' | 'eticket') => {
    setActiveModal(type);
  };

  const closeModal = () => {
    setActiveModal(null);
  };

  // CHANGED: Function to hide web UI - runs after page loads
  const hideWebUI = () => {
    const jsCode = `
      (function() {
        // Wait for DOM to be ready
        setTimeout(function() {
          // Hide all UI containers including Enhanced Map Controls
          var elementsToHide = [
            '.header',
            '.department-info', 
            '.stats-container',
            '.control-panel',
            '.eticket-button',
            'button:not(.leaflet-control button)',
            '.leaflet-top.leaflet-right > div:not(.leaflet-control-zoom)',
            'div[style*="position: absolute"]:not(#map):not([id*="leaflet"])',
            'div:has(> h3)',
            'div:has(> button)',
            '[class*="enhanced"]',
            '[class*="control"]'
          ];
          
          elementsToHide.forEach(function(selector) {
            var elements = document.querySelectorAll(selector);
            elements.forEach(function(el) {
              // Don't hide leaflet map controls
              if (!el.classList.contains('leaflet-control') && 
                  !el.closest('.leaflet-control') &&
                  el.id !== 'map') {
                el.style.display = 'none';
              }
            });
          });
          
          // Hide all divs that are positioned absolutely (except map and leaflet)
          var allDivs = document.querySelectorAll('div');
          allDivs.forEach(function(div) {
            var style = window.getComputedStyle(div);
            if (style.position === 'absolute' && 
                div.id !== 'map' && 
                !div.classList.contains('leaflet-control') &&
                !div.closest('.leaflet-control') &&
                !div.closest('#map')) {
              div.style.display = 'none';
            }
          });
          
          // Make map full screen
          var mapEl = document.getElementById('map');
          if (mapEl) {
            mapEl.style.position = 'fixed';
            mapEl.style.top = '0';
            mapEl.style.left = '0';
            mapEl.style.width = '100vw';
            mapEl.style.height = '100vh';
            mapEl.style.zIndex = '1';
          }
          
          // Clean up body
          document.body.style.margin = '0';
          document.body.style.padding = '0';
          document.body.style.overflow = 'hidden';
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

  return (
    <View style={s.container}>
      {/* Full Screen Map - Web UI Hidden */}
      <WebView
        ref={webviewRef}
        source={{uri: 'http://10.0.2.2:8000/map'}}
        style={s.webview}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        startInLoadingState={true}
        onLoadEnd={hideWebUI} // CHANGED: Run after page loads
        renderLoading={() => (
          <View style={s.center}>
            <ActivityIndicator size="large" color="#1565C0" />
            <Text style={s.loadTxt}>Loading Map...</Text>
          </View>
        )}
      />

      {/* Compact Header Bar */}
      <View style={s.topBar}>
        <Text style={s.topTitle}>🚌 Metro Live</Text>
        <TouchableOpacity style={s.refreshBtn} onPress={fetchBuses}>
          <Text style={s.refreshTxt}>🔄</Text>
        </TouchableOpacity>
      </View>

      {/* Floating Action Buttons - CHANGED: Only 2 buttons */}
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

      {/* Modal Container */}
      {activeModal !== null && (
        <TouchableOpacity
          style={s.modalOverlay}
          activeOpacity={1}
          onPress={closeModal}>
          <TouchableOpacity
            activeOpacity={1}
            style={[s.modalContent]}
            onPress={(e) => e.stopPropagation()}>
            <Animated.View
              style={[
                s.modalContentInner,
                {transform: [{translateY: slideAnim}]},
              ]}>
              {/* Modal Header */}
              <View style={s.modalHeader}>
                <View style={s.modalHandle} />
                <Text style={s.modalTitle}>
                  {activeModal === 'list' && '📋 Bus List'}
                  {activeModal === 'eticket' && '🎫 E-Ticket'}
                </Text>
                <TouchableOpacity style={s.closeBtn} onPress={closeModal}>
                  <Text style={s.closeTxt}>✕</Text>
                </TouchableOpacity>
              </View>

              {/* Modal Body */}
              <ScrollView style={s.modalBody}>
                {/* Bus List Modal - CHANGED: Now shows content */}
                {activeModal === 'list' && (
                  <View>
                    {buses.length === 0 ? (
                      <View style={s.emptyState}>
                        <Text style={s.emptyText}>No active buses</Text>
                        <Text style={s.emptySubtext}>
                          Activate buses from web admin panel
                        </Text>
                      </View>
                    ) : (
                      buses.map((bus, i) => (
                        <View key={bus.bus_id || i} style={s.card}>
                          <View style={s.cardHead}>
                            <Text style={s.cardId}>{bus.bus_id}</Text>
                            <View
                              style={[
                                s.badge,
                                bus.bus_id?.includes('-F-')
                                  ? s.fBadge
                                  : s.rBadge,
                              ]}>
                              <Text style={s.badgeTxt}>
                                {bus.bus_id?.includes('-F-') ? '▶ FWD' : '◀ REV'}
                              </Text>
                            </View>
                          </View>
                          <Text style={s.cardRoute}>Route: {bus.route_id}</Text>
                          {bus.speed != null && (
                            <Text style={s.cardSpeed}>
                              ⚡ {Number(bus.speed).toFixed(1)} km/h
                            </Text>
                          )}
                          <Text style={s.cardCoord}>
                            📍 {bus.current_lat?.toFixed(4)},{' '}
                            {bus.current_lng?.toFixed(4)}
                          </Text>
                        </View>
                      ))
                    )}
                  </View>
                )}

                {/* E-Ticket Modal - CHANGED: Now shows content */}
                {activeModal === 'eticket' && (
                  <View style={s.eticketContainer}>
                    <Text style={s.eticketTitle}>
                      Purchase Metro Bus E-Ticket
                    </Text>
                    <TouchableOpacity style={s.eticketBtn}>
                      <Text style={s.eticketBtnTxt}>Login / Sign Up</Text>
                    </TouchableOpacity>
                    <Text style={s.eticketInfo}>
                      🎉 Senior citizens (60+) travel FREE!
                    </Text>
                    <View style={s.infoBox}>
                      <Text style={s.infoText}>
                        💳 Top-up available via EasyPaisa, JazzCash, NayaPay, SadaPay
                      </Text>
                      <Text style={s.infoText}>
                        💰 Fare: Rs. 10/km (Minimum Rs. 20)
                      </Text>
                    </View>
                  </View>
                )}
              </ScrollView>
            </Animated.View>
          </TouchableOpacity>
        </TouchableOpacity>
      )}
    </View>
  );
};

const s = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#000'},
  center: {flex: 1, justifyContent: 'center', alignItems: 'center'},
  loadTxt: {marginTop: 10, fontSize: 16, color: '#666'},
  webview: {flex: 1},

  // Top Bar
  topBar: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(21, 101, 192, 0.95)',
    paddingHorizontal: 16,
    paddingTop: 44,
    paddingBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    zIndex: 10,
  },
  topTitle: {fontSize: 16, fontWeight: 'bold', color: '#fff'},
  refreshBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  refreshTxt: {fontSize: 16},

  // Floating Action Buttons
  fabContainer: {
    position: 'absolute',
    right: 16,
    top: 120,
    gap: 12,
    zIndex: 10,
  },
  fab: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#1565C0',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  fabActive: {
    backgroundColor: '#0D47A1',
    transform: [{scale: 1.1}],
  },
  fabIcon: {fontSize: 24},

  // Modal
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    zIndex: 20,
    justifyContent: 'flex-end',
  },
  modalContent: {
    width: '100%',
    maxHeight: SCREEN_HEIGHT * 0.75,
  },
  modalContentInner: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: SCREEN_HEIGHT * 0.75,
    elevation: 10,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  modalHandle: {
    position: 'absolute',
    top: 8,
    left: '50%',
    marginLeft: -20,
    width: 40,
    height: 4,
    backgroundColor: '#ccc',
    borderRadius: 2,
  },
  modalTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: 'bold',
    color: '#222',
    textAlign: 'center',
  },
  closeBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeTxt: {fontSize: 18, color: '#666'},
  modalBody: {
    flex: 1,
    padding: 16,
  },

  // Empty State
  emptyState: {
    alignItems: 'center',
    paddingVertical: 48,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#999',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#bbb',
    textAlign: 'center',
  },

  // Bus List
  card: {
    backgroundColor: '#fff',
    marginBottom: 12,
    padding: 12,
    borderRadius: 10,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#eee',
  },
  cardHead: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  cardId: {fontSize: 14, fontWeight: 'bold', color: '#222', flex: 1},
  badge: {paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8},
  fBadge: {backgroundColor: '#E8F5E9'},
  rBadge: {backgroundColor: '#FBE9E7'},
  badgeTxt: {fontSize: 11, fontWeight: 'bold', color: '#333'},
  cardRoute: {fontSize: 12, color: '#2196F3', marginBottom: 2},
  cardSpeed: {fontSize: 12, color: '#FF9800', marginBottom: 2},
  cardCoord: {fontSize: 11, color: '#999'},

  // E-Ticket
  eticketContainer: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  eticketTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#222',
    marginBottom: 24,
    textAlign: 'center',
  },
  eticketBtn: {
    backgroundColor: '#1565C0',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 25,
    elevation: 3,
    marginBottom: 16,
  },
  eticketBtnTxt: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  eticketInfo: {
    fontSize: 14,
    color: '#4CAF50',
    textAlign: 'center',
    marginBottom: 16,
  },
  infoBox: {
    backgroundColor: '#E3F2FD',
    padding: 16,
    borderRadius: 8,
    marginTop: 8,
    width: '100%',
  },
  infoText: {
    fontSize: 13,
    color: '#1565C0',
    marginBottom: 4,
  },
});

export default MapScreen;
