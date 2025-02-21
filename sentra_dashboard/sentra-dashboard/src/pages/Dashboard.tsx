import { Box, Container, Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import mapboxgl from 'mapbox-gl';
import { useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

// Replace with your Mapbox access token
const MAPBOX_TOKEN = 'pk.eyJ1IjoiYWxsZXJpbiIsImEiOiJjbTdld3AwZG0waWN5Mm1xM203eXlqeG5nIn0.tM4ISdCOSIdxir2zpywssg';

// RTK Query API for traffic analytics and entries
const trafficApi = createApi({
  reducerPath: 'trafficApi',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:3000/api/v1/',
    prepareHeaders: (headers) => {
      headers.set('Authorization', 'Bearer cfbb852abff15c0e19ac12fc5f902de7');
      return headers;
    },
  }),
  endpoints: (builder) => ({
    getTrafficAnalytics: builder.query<Record<string, number>, void>({
      query: () => 'traffic_analytics',
      transformResponse: (response: { status: string; data: Record<string, number> }) => {
        if (response.status !== 'success') {
          console.error('Unexpected API response', response);
          return {};
        }
        return response.data;
      },
    }),
    getTrafficEntries: builder.query<any[], void>({
      query: () => 'traffic_data',
      transformResponse: (response: { status: string; data: any[] }) => {
        if (response.status !== 'success') {
          console.error('Unexpected API response for traffic entries', response);
          return [];
        }
        return response.data;
      },
    }),
  }),
});

// Redux store setup
const store = configureStore({
  reducer: {
    [trafficApi.reducerPath]: trafficApi.reducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(trafficApi.middleware),
});

// Wrap Dashboard with Redux Provider (for RTK Query)
const DashboardWrapper = () => (
  <Provider store={store}>
    <Dashboard />
  </Provider>
);

const Dashboard = () => {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markers = useRef<mapboxgl.Marker[]>([]);

  const {
    data: analytics,
    isLoading: analyticsLoading,
    isError: analyticsError,
  } = trafficApi.endpoints.getTrafficAnalytics.useQuery();

  const {
    data: trafficEntries,
    isLoading: entriesLoading,
    isError: entriesError,
  } = trafficApi.endpoints.getTrafficEntries.useQuery();

  // Prepare chart data from analytics; log if data format is unexpected
  const chartData =
    analytics && typeof analytics === 'object'
      ? Object.entries(analytics).map(([name, value]) => ({ name, value: Number(value) || 0 }))
      : [{ name: 'No data', value: 0 }];
  if (!analyticsLoading && !analyticsError && analytics && typeof analytics !== 'object') {
    console.error('Analytics data format error', analytics);
  }

  useEffect(() => {
    if (!mapContainer.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [0, 0], // Default center (adjust as needed)
      zoom: 2, // Default zoom level
    });

    // Connect to Rails ActionCable via Socket.IO with enhanced debugging
    const socket = io('ws://localhost:3000', {
      path: '/cable', // ActionCable default path
      transports: ['websocket'],
      secure: false, // Explicitly allow non-secure WebSocket (ws://) for localhost
      reconnection: true, // Enable reconnection attempts
      reconnectionAttempts: 10, // Increased reconnection attempts
      reconnectionDelay: 2000, // Increased delay between reconnection attempts (2 seconds)
      timeout: 5000, // Set timeout for connection attempts
    });

    socket.on('connect', () => {
      console.log('WebSocket connected to ActionCable successfully');
    });

    socket.on('connect_error', (err) => {
      console.error('WebSocket connection error:', err.message, 'Retrying...');
    });

    socket.on('traffic_updates', (data: { traffic_entry: any }) => {
      if (data.traffic_entry && map.current) {
        const { device_id, center_x, center_y } = data.traffic_entry;
        const lat = center_y / 100; // Ensure conversion is correct
        const lng = center_x / 100; // Ensure conversion is correct

        console.log('Received traffic update:', { device_id, lat, lng });

        // Remove existing marker for this device_id if it exists
        markers.current = markers.current.filter(marker =>
          (marker.getPopup()?.getElement()?.textContent || '').includes(device_id)
        );

        // Add new marker with improved positioning and styling
        const marker = new mapboxgl.Marker({ color: '#FF0000' }) // Red marker for visibility
          .setLngLat([lng, lat])
          .setPopup(new mapboxgl.Popup({ offset: 25 }).setHTML(`Device: ${device_id}`))
          .addTo(map.current);

        markers.current.push(marker);
      }
    });

    // Cleanup on unmount
    return () => {
      if (map.current) map.current.remove();
      if (socket.connected) socket.disconnect();
    };
  }, []);

  // Define columns for the Data Grid
  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 90 },
    { field: 'timestamp', headerName: 'Timestamp', width: 200, valueFormatter: (params: { value: string | number }) => new Date(params.value).toLocaleString() },
    { field: 'device_id', headerName: 'Device ID', width: 150 },
    { field: 'object_type', headerName: 'Object Type', width: 120 },
    { field: 'confidence', headerName: 'Confidence', width: 120, type: 'number', valueFormatter: (params: { value: number }) => `${params.value}%` },
    { field: 'center_x', headerName: 'Center X', width: 120, type: 'number' },
    { field: 'center_y', headerName: 'Center Y', width: 120, type: 'number' },
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4, p: 2 }}> {/* Added padding for better spacing */}
        <Typography variant="h4" component="h1" gutterBottom>
          SENTRA Dashboard
        </Typography>
        <Typography variant="body1" sx={{ mb: 4 }}>
          Welcome to the real-time traffic monitoring and analytics dashboard. Live data and charts will be displayed here!
        </Typography>
        <Box
          ref={mapContainer}
          sx={{ height: '400px', width: '100%', mt: 4, mb: 4 }}
        />
        {analyticsLoading && <Typography>Loading analytics...</Typography>}
        {analyticsError && <Typography>Error loading analytics: Unknown error</Typography>}
        {!analyticsLoading && !analyticsError && chartData.length > 0 && (
          <Box sx={{ mt: 8, mb: 6, width: '100%', maxWidth: '1200px', mx: 'auto' }}> {/* Increased margins, max width, and centered */}
            <Typography variant="h6" sx={{ mb: 4, ml: 2, color: '#1976D2' }}> {/* Enhanced styling for visibility */}
              Traffic Analytics
            </Typography>
            <BarChart width={900} height={450} data={chartData} style={{ margin: 'auto' }}> {/* Increased size for better visibility */}
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </Box>
        )}
        {entriesLoading && <Typography>Loading traffic entries...</Typography>}
        {entriesError && <Typography>Error loading traffic entries: Unknown error</Typography>}
        {!entriesLoading && !entriesError && trafficEntries && trafficEntries.length > 0 && (
          <Box sx={{ mt: 4, mb: 4, width: '100%', maxWidth: '1200px', mx: 'auto' }}>
            <Typography variant="h6" sx={{ mb: 2, ml: 2, color: '#1976D2' }}>
              Traffic Entries
            </Typography>
            <DataGrid
              rows={trafficEntries}
              columns={columns}
              initialState={{
                pagination: {
                  paginationModel: { page: 0, pageSize: 5 },
                },
              }}
              pageSizeOptions={[5, 10]}
              checkboxSelection
              disableRowSelectionOnClick
              sx={{ bgcolor: 'white', borderRadius: 2, boxShadow: 1 }}
            />
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default DashboardWrapper;