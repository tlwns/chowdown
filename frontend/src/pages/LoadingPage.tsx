import { Box, Center, Spinner, Text, VStack } from '@chakra-ui/react';

const LoadingPage = () => {
  return (
    <>
      <Center flex={1} bg="chowdownPurple.50">
        <VStack gap="4">
          <Spinner size="xl" />
          <Box>
            <Text>fetching data...</Text>
          </Box>
        </VStack>
      </Center>
    </>
  );
};

export default LoadingPage;
