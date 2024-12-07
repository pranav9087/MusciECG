import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Button } from 'react-native';
import * as FileSystem from 'expo-file-system';
import axios from 'axios';

const { StorageAccessFramework } = FileSystem;

export default function App() {
  const [emotions, setEmotions] = useState([]);
  const [error, setError] = useState(null);
  const [foundFiles, setFoundFiles] = useState([]);
  const [directoryUri, setDirectoryUri] = useState(null);

  const SERVER_URL = 'http://10.192.160.180:8000/process_ecg';

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
      console.log(entries.length);
      for (const entry of entries) {
        if (entry.endsWith('.csv')) {
          console.log('Found CSV file:', entry);
          csvFiles.push(entry);
        }
      }
    } catch (error) {
      console.error(`Error reading directory ${directoryUri}:`, error);
    }

    console.log(`Total CSV files found: ${csvFiles.length}`);
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
      console.log('Detected emotions', response.data.emotions);
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

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>ECG Emotion Monitor</Text>
      
      {(
        <Button title="Select ECG" onPress={requestSAFPermission} />
      )}

      {error && <Text style={styles.error}>{error}</Text>}

      <View style={styles.filesContainer}>
        <Text style={styles.subtitle}>Files Found ({foundFiles.length}):</Text>
        {foundFiles.map((file, index) => (
          <Text key={index} style={styles.file}>
            {file.split('/').slice(-2).join('/')}
          </Text>
        ))}
      </View>
      
      <View style={styles.emotionsContainer}>
        <Text style={styles.subtitle}>Detected Emotions:</Text>
        {emotions.map((item, index) => (
          <View key={index} style={styles.emotionItem}>
            <Text style={styles.emotion}>{item}</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  error: {
    color: 'red',
    marginBottom: 10,
  },
  filesContainer: {
    marginBottom: 20,
  },
  emotionsContainer: {
    marginTop: 20,
  },
  subtitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  fileItem: {
    marginBottom: 15,
    padding: 10,
    backgroundColor: '#f5f5f5',
    borderRadius: 5,
  },
  file: {
    fontSize: 14,
    color: '#333',
    fontWeight: 'bold',
  },
  fileDetails: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  emotion: {
    fontSize: 16,
    marginBottom: 5,
  },
  noFiles: {
    fontSize: 14,
    fontStyle: 'italic',
    color: '#666',
  }
});