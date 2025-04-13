
import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  colors: {
    brand: {
      50: '#E8F5E9',
      100: '#C8E6C9',
      200: '#A5D6A7',
      300: '#81C784',
      400: '#66BB6A',
      500: '#000', // Primary cute green shade 4CAF50
      600: '#000', //#43A047
      700: '#388E3C',
      800: '#2E7D32',
      900: '#1B5E20',
    },
    accent: {
      50: '#FFF9E6',
      100: '#FFF3CC',
      200: '#FFE799',
      300: '#FFDB66',
      400: '#FFCF33',
      500: '#FFC300',
      600: '#CC9C00',
      700: '#997500',
      800: '#664E00',
      900: '#332700',
    },
  },
  fonts: {
    heading: '"Inter", sans-serif',
    body: '"Inter", sans-serif',
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: 'bold',
        borderRadius: 'md',
      },
      variants: {
        primary: {
          bg: 'brand.500',
          color: 'white',
          _hover: {
            bg: 'brand.600',
            _disabled: {
              bg: 'brand.500',
            },
          },
        },
        secondary: {
          bg: 'accent.500',
          color: 'black',
          _hover: {
            bg: 'accent.400',
            _disabled: {
              bg: 'accent.500',
            },
          },
        },
        outline: {
          borderColor: 'brand.500',
          color: 'brand.500',
        },
      },
    },
    Input: {
      defaultProps: {
        focusBorderColor: 'brand.500',
      },
    },
  },
  styles: {
    global: {
      body: {
        bg: 'gray.50',
        color: 'gray.800',
      },
    },
  },
});

export default theme;
