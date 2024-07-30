import { Box, Button, HStack, Text, VStack, useToken } from '@chakra-ui/react';
import React from 'react';

const RANGE = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900];

const DISPLAYED: { scheme: string; semantic: string }[] = [
  { scheme: 'chowdownGunmetal', semantic: 'chowdown.gunmetal' },
  { scheme: 'chowdownGray', semantic: 'chowdown.gray' },
  { scheme: 'chowdownPurple', semantic: 'chowdown.purple' },
  { scheme: 'chowdownLavender', semantic: 'chowdown.lavender' },
  { scheme: 'chowdownPink', semantic: 'chowdown.pink' }
];

const Spectrum: React.FC<{ scheme: string; bg: string }> = ({ scheme, bg }) => {
  const tokens = useToken(
    'color',
    RANGE.map((n) => `${scheme}.${n}`)
  );

  return (
    // 1 means 0.25rem, at 16px root em, so 4px
    <HStack background={bg} padding="2" spacing="0" borderRadius="base">
      {tokens.map((token) => (
        <Box key={token} background={token} padding="4" />
      ))}
    </HStack>
  );
};

const ThemingPlayground: React.FC = () => {
  return (
    <VStack align="flex-start">
      {DISPLAYED.map(({ scheme, semantic }) => (
        <VStack key={scheme} align="flex-start">
          <HStack>
            <Button variant="solid" colorScheme={scheme}>
              solid
            </Button>
            <Button variant="outline" colorScheme={scheme}>
              outline
            </Button>
            <Button variant="ghost" colorScheme={scheme}>
              ghost
            </Button>
            <Button variant="link" colorScheme={scheme}>
              link
            </Button>
            <Text color={semantic}>{semantic}</Text>
          </HStack>
          <HStack>
            <Spectrum scheme={scheme} bg="white" />
            <Spectrum scheme={scheme} bg="black" />
          </HStack>
        </VStack>
      ))}
    </VStack>
  );
};

export default ThemingPlayground;
