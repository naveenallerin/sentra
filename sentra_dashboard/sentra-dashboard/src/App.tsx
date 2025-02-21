import { ThemeProvider, createTheme } from '@mui/material';
import Dashboard from './pages/Dashboard';

const theme = createTheme();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Dashboard />
    </ThemeProvider>
  );
}

export default App;