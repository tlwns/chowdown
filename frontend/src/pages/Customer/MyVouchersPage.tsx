import {
  Box,
  Button,
  ButtonGroup,
  HStack,
  Heading,
  Text,
  VStack
} from '@chakra-ui/react';
import { Link, Outlet, useLocation } from 'react-router-dom';

const MyVouchers = () => {
  //  Get which child route is being rendered (subpage of eatery page)
  const { pathname } = useLocation();
  const subPageDisplaying = pathname.split('/').pop();

  const subPages = [
    ['', 'Current'],
    ['past-vouchers', 'Past']
  ];

  return (
    <VStack
      flex={1}
      bg="chowdownPurple.50"
      px={{ base: 4, sm: 14 }}
      py={5}
      gap={10}
      height={'100%'}
      align={{ base: 'center', md: 'flex-start' }}>
      <Heading as={Text} align={'center'} px={20}>
        My Vouchers
      </Heading>
      <HStack w={'100%'} justify={{ base: 'center', md: 'flex-end' }}>
        <ButtonGroup>
          {/* Subpage buttons */}
          {subPages.map(([route, label]) => (
            <Button
              as={Link}
              to={route}
              key={route}
              width={100}
              colorScheme={
                subPageDisplaying === route ||
                (subPageDisplaying === 'my-vouchers' && route === '')
                  ? 'chowdownGray'
                  : undefined
              }
              borderRadius="full">
              {label}
            </Button>
          ))}
        </ButtonGroup>
      </HStack>

      <Box flex={1} width={'100%'}>
        <Outlet />
      </Box>
    </VStack>
  );
};

export default MyVouchers;
