import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, FlatList, Dimensions } from 'react-native';
import { WebView } from 'react-native-webview';
import * as FileSystem from 'expo-file-system';
import axios from 'axios';

const { StorageAccessFramework } = FileSystem;

export default function App() {
  const [emotions, setEmotions] = useState([]);
  const [songs, setSongs] = useState([]);
  const [error, setError] = useState(null);
  const [foundFiles, setFoundFiles] = useState([]);
  const [directoryUri, setDirectoryUri] = useState(null);

  const SERVER_URL = 'http://192.168.10.157:8000/process_ecg';

  const requestSAFPermission = async () => {
    try {
      const permissions = await StorageAccessFramework.requestDirectoryPermissionsAsync();
      if (permissions.granted) {
        setDirectoryUri(permissions.directoryUri);
      } else {
        setError('Permission to access directory was denied');
      }
    } catch (err) {
      setError('Error requesting permissions: ' + err.message);
    }
  };

  const findCsvFiles = async (directoryUri) => {
    const csvFiles = [];
    try {
      const entries = await FileSystem.StorageAccessFramework.readDirectoryAsync(directoryUri);
      for (const entry of entries) {
        if (entry.endsWith('.csv')) {
          csvFiles.push(entry);
        }
      }
    } catch (error) {
      console.error(`Error reading directory ${directoryUri}:`, error);
    }
    return csvFiles;
  };

  const processNewFile = async (fileUri) => {
    try {
      const fileContent = await FileSystem.readAsStringAsync(fileUri, { encoding: FileSystem.EncodingType.UTF8 });
      
      const response = await axios.post(SERVER_URL, {
        ecgData: fileContent,
        filename: fileUri.split('/').pop()
      });
      
      setEmotions(response.data.emotions);
      setSongs(response.data.songs || []);
    } catch (err) {
      setError(`Error processing file ${fileUri}: ${err.message}`);
    }
  };

  useEffect(() => {
    if (directoryUri) {
      const checkForNewFiles = async () => {
        try {
          const csvFiles = await findCsvFiles(directoryUri);
          setFoundFiles(csvFiles);
          for (const fileUri of csvFiles) {
            await processNewFile(fileUri);
          }
        } catch (err) {
          setError('Error checking for files: ' + err.message);
        }
      };

      checkForNewFiles();
    }
  }, [directoryUri]);

  const renderSong = ({ item }) => {
    return (
      <View style={styles.songPreview}>
        <WebView
          source={{ uri: item }}
          style={styles.videoPlayer}
          javaScriptEnabled={true}
          domStorageEnabled={true}
        />
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>ECG Emotion Monitor</Text>
      </View>

      <ScrollView style={styles.content}>
        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.error}>{error}</Text>
          </View>
        )}

        <View style={styles.emotionsContainer}>
          <Text style={styles.subtitle}>Detected Emotions</Text>
          {emotions.length > 0 ? (
            emotions.map((item, index) => (
              <View key={index} style={styles.emotionItem}>
                <Text style={styles.emotion}>{item}</Text>
              </View>
            ))
          ) : (
            <Text style={styles.noDataText}>No emotions detected yet.</Text>
          )}
        </View>

        {songs.length > 0 && (
          <View style={styles.songsContainer}>
            <Text style={styles.subtitle}>Recommended Songs</Text>
            <FlatList
              data={songs}
              renderItem={renderSong}
              keyExtractor={(item, index) => `${item}-${index}`}
              horizontal={true}
              showsHorizontalScrollIndicator={false}
            />
          </View>
        )}
      </ScrollView>

      <TouchableOpacity style={styles.selectButton} onPress={requestSAFPermission}>
        <Text style={styles.selectButtonText}>Select ECG Directory</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  header: {
    paddingVertical: 30,
    backgroundColor: '#6200ee',
    alignItems: 'center',
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 4,
  },
  title: {
    fontSize: 28,
    color: '#fff',
    fontWeight: 'bold',
    marginTop: 25,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  errorContainer: {
    marginHorizontal: 10,
    padding: 15,
    backgroundColor: '#ffe0e0',
    borderRadius: 10,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  error: {
    color: '#d32f2f',
    fontSize: 16,
    textAlign: 'center',
  },
  emotionsContainer: {
    marginTop: 20,
  },
  subtitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
    textAlign: 'center',
  },
  emotionItem: {
    backgroundColor: '#e8f5e9',
    padding: 15,
    marginBottom: 10,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  emotion: {
    fontSize: 18,
    fontWeight: '500',
    color: '#2e7d32',
  },
  noDataText: {
    fontSize: 16,
    fontStyle: 'italic',
    color: '#999',
    textAlign: 'center',
    marginTop: 20,
  },
  songsContainer: {
    marginTop: 20,
  },
  songPreview: {
    width: Dimensions.get('window').width * 0.9,
    height: 290,
    marginRight: 10,
    borderRadius: 10,
    overflow: 'hidden',
    backgroundColor: '#000',
  },
  videoPlayer: {
    flex: 1,
  },
  selectButton: {
    backgroundColor: '#03dac6',
    padding: 15,
    borderRadius: 30,
    alignItems: 'center',
    position: 'absolute',
    bottom: 20,
    left: '50%',
    transform: [{ translateX: -150 }],
    width: 300,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 3,
  },
  selectButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
});