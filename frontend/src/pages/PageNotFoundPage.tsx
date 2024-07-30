import { VStack, Heading, Text, Code } from '@chakra-ui/react';
import { useLocation } from 'react-router-dom';
const PageNotFoundPage = () => {
  const location = useLocation();
  console.log(location);
  return (
    <VStack h="100vh" align={'center'} justify={'center'}>
      <Heading color="chowdown.">404 Page Not Found</Heading>
      <Text>
        Sorry, we couldn&quot;t find the page you were looking for at{' '}
        <Code>{location.pathname}</Code>
      </Text>
      <Text fontSize={'6xl'}>🍽️</Text>
    </VStack>
  );
};

export default PageNotFoundPage;
