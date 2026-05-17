import React, {useState} from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';

const API_URL = 'http://10.0.2.2:8000';

interface Props {
  onSignupSuccess: (user: any) => void;
  onGoToLogin: () => void;
  onClose: () => void;
}

const SignupScreen = ({onSignupSuccess, onGoToLogin, onClose}: Props) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [age, setAge] = useState('');
  const [loading, setLoading] = useState(false);

  const isSenior = parseInt(age) >= 60;

  const handleSignup = async () => {
    if (!name.trim() || !email.trim() || !password.trim() || !age.trim()) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }
    const ageNum = parseInt(age);
    if (isNaN(ageNum) || ageNum < 1 || ageNum > 120) {
      Alert.alert('Error', 'Please enter a valid age');
      return;
    }
    if (password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/eticket/signup`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
          password,
          age: ageNum,
          phone: '',
        }),
      });
      const data = await res.json();

      if (res.ok && data.success) {
        onSignupSuccess(data.user);
      } else {
        Alert.alert('Signup Failed', data.message || 'Could not create account');
      }
    } catch (e) {
      Alert.alert('Error', 'Could not connect to server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={{flex: 1}}>
      <ScrollView
        contentContainerStyle={styles.container}
        keyboardShouldPersistTaps="handled">

        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity style={styles.backBtn} onPress={onClose}>
            <Text style={styles.backTxt}>✕</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>📝 Create Account</Text>
          <View style={{width: 32}} />
        </View>

        {/* Form */}
        <View style={styles.form}>
          <Text style={styles.formTitle}>Join Metro Bus 360</Text>
          <Text style={styles.formSubtitle}>Create your e-ticket account</Text>

          <Text style={styles.label}>Full Name</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter your full name"
            placeholderTextColor="#aaa"
            value={name}
            onChangeText={setName}
          />

          <Text style={styles.label}>Email Address</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter your email"
            placeholderTextColor="#aaa"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />

          <Text style={styles.label}>Password</Text>
          <TextInput
            style={styles.input}
            placeholder="Minimum 6 characters"
            placeholderTextColor="#aaa"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          <Text style={styles.label}>Age</Text>
          <TextInput
            style={[styles.input, isSenior && styles.inputSenior]}
            placeholder="Enter your age"
            placeholderTextColor="#aaa"
            value={age}
            onChangeText={setAge}
            keyboardType="numeric"
            maxLength={3}
          />

          {/* Senior citizen banner */}
          {isSenior && (
            <View style={styles.seniorBanner}>
              <Text style={styles.seniorBannerText}>
                🎉 You qualify for FREE travel as a senior citizen!
              </Text>
            </View>
          )}

          <TouchableOpacity
            style={[styles.signupBtn, loading && {opacity: 0.7}]}
            onPress={handleSignup}
            disabled={loading}>
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.signupBtnTxt}>Create Account</Text>
            )}
          </TouchableOpacity>

          <View style={styles.divider}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerTxt}>Already have an account?</Text>
            <View style={styles.dividerLine} />
          </View>

          <TouchableOpacity style={styles.loginBtn} onPress={onGoToLogin}>
            <Text style={styles.loginBtnTxt}>Login Instead</Text>
          </TouchableOpacity>

          <View style={styles.infoBox}>
            <Text style={styles.infoText}>💰 Fare: Rs. 10/km (Min Rs. 20)</Text>
            <Text style={styles.infoText}>👴 Age 60+ = FREE travel</Text>
            <Text style={styles.infoText}>💳 Top-up via EasyPaisa, JazzCash & more</Text>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  backBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  backTxt: {fontSize: 16, color: '#666'},
  headerTitle: {
    flex: 1,
    textAlign: 'center',
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1565C0',
  },
  form: {
    paddingHorizontal: 24,
    paddingBottom: 32,
    paddingTop: 16,
  },
  formTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1565C0',
    marginBottom: 4,
  },
  formSubtitle: {
    fontSize: 13,
    color: '#888',
    marginBottom: 16,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: '#444',
    marginBottom: 6,
    marginTop: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 15,
    color: '#222',
    backgroundColor: '#fafafa',
  },
  inputSenior: {
    borderColor: '#4CAF50',
    backgroundColor: '#F1F8E9',
  },
  seniorBanner: {
    backgroundColor: '#E8F5E9',
    borderRadius: 8,
    padding: 12,
    marginTop: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  seniorBannerText: {
    color: '#2E7D32',
    fontSize: 13,
    fontWeight: '600',
  },
  signupBtn: {
    backgroundColor: '#1565C0',
    borderRadius: 25,
    paddingVertical: 15,
    alignItems: 'center',
    marginTop: 24,
    elevation: 3,
  },
  signupBtnTxt: {color: '#fff', fontSize: 16, fontWeight: 'bold'},
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 20,
  },
  dividerLine: {flex: 1, height: 1, backgroundColor: '#eee'},
  dividerTxt: {marginHorizontal: 12, color: '#aaa', fontSize: 12},
  loginBtn: {
    borderWidth: 2,
    borderColor: '#1565C0',
    borderRadius: 25,
    paddingVertical: 13,
    alignItems: 'center',
  },
  loginBtnTxt: {color: '#1565C0', fontSize: 15, fontWeight: 'bold'},
  infoBox: {
    backgroundColor: '#E3F2FD',
    padding: 16,
    borderRadius: 8,
    marginTop: 24,
    gap: 6,
  },
  infoText: {fontSize: 13, color: '#1565C0'},
});

export default SignupScreen;
