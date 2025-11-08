import { createTheme } from '@mui/material/styles';

/**
 * Custom MUI theme with Google color palette
 * Colors: Blue #4285F4, Red #EA4335, Yellow #FBBC04, Green #34A853
 */
export const theme = createTheme({
  palette: {
    primary: {
      main: '#4285F4', // Google Blue
      light: '#669DF6',
      dark: '#1967D2',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#34A853', // Google Green
      light: '#5BB974',
      dark: '#0D652D',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#EA4335', // Google Red
      light: '#EE675C',
      dark: '#C5221F',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#FBBC04', // Google Yellow
      light: '#FCC934',
      dark: '#F29900',
      contrastText: '#000000',
    },
    info: {
      main: '#4285F4',
      light: '#669DF6',
      dark: '#1967D2',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#34A853',
      light: '#5BB974',
      dark: '#0D652D',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FFFFFF',
      paper: '#F8F9FA',
    },
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.6)',
      disabled: 'rgba(0, 0, 0, 0.38)',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 500,
      fontSize: 'clamp(2rem, 5vw, 2.5rem)',
      lineHeight: 1.2,
    },
    h2: {
      fontWeight: 500,
      fontSize: 'clamp(1.75rem, 4vw, 2rem)',
      lineHeight: 1.3,
    },
    h3: {
      fontWeight: 500,
      fontSize: 'clamp(1.5rem, 3.5vw, 1.75rem)',
      lineHeight: 1.4,
    },
    h4: {
      fontWeight: 500,
      fontSize: 'clamp(1.25rem, 3vw, 1.5rem)',
      lineHeight: 1.4,
    },
    h5: {
      fontWeight: 500,
      fontSize: 'clamp(1.1rem, 2.5vw, 1.25rem)',
      lineHeight: 1.5,
    },
    h6: {
      fontWeight: 500,
      fontSize: 'clamp(1rem, 2vw, 1.125rem)',
      lineHeight: 1.6,
    },
    body1: {
      fontSize: 'clamp(0.875rem, 2vw, 1rem)',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: 'clamp(0.8125rem, 1.8vw, 0.875rem)',
      lineHeight: 1.43,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
      fontSize: 'clamp(0.875rem, 2vw, 1rem)',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          padding: '10px 20px',
          minHeight: '44px', // Touch-friendly minimum height
          fontSize: '0.875rem',
          fontWeight: 500,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.15)',
          },
        },
        sizeLarge: {
          padding: '14px 28px',
          minHeight: '48px', // Larger touch target for primary actions
          fontSize: '1rem',
        },
        sizeSmall: {
          padding: '6px 12px',
          minHeight: '36px',
          fontSize: '0.8125rem',
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          minWidth: '44px', // Touch-friendly minimum width
          minHeight: '44px', // Touch-friendly minimum height
          padding: '10px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.08)',
          '&:hover': {
            boxShadow: '0px 4px 16px rgba(0, 0, 0, 0.12)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
        elevation1: {
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.08)',
        },
        elevation2: {
          boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.08)',
        },
        elevation3: {
          boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          fontWeight: 500,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 12,
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          height: 8,
        },
      },
    },
  },
});
