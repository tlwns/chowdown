import React from 'react';
import ReactDOM from 'react-dom/client';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';

import './utils/api/config';
import './index.css';
import chowdownTheme from './utils/theme.ts';

import App from './App.tsx';
import TokenProvider from './context/TokenProvider.tsx';

// https://chakra-ui.com/docs/styled-system/semantic-tokens
const extendedTheme = extendTheme(chowdownTheme);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ChakraProvider theme={extendedTheme}>
      <TokenProvider>
        <App />
      </TokenProvider>
    </ChakraProvider>
  </React.StrictMode>
);
