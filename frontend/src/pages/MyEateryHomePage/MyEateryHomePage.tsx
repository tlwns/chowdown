import {
  Box,
  Button,
  Flex,
  Heading,
  Image,
  Text,
  VStack
} from '@chakra-ui/react';
import { Outlet, useLocation } from 'react-router-dom';

import { Link } from 'react-router-dom';
import { AuthContext } from '../../context/authContext';
import { useContext } from 'react';
import { getEateryPublicDetails } from '../../utils/api/eateries';
import LoadingPage from '../LoadingPage';
import { useQuery } from '@tanstack/react-query';

const MyEateryHomePage = () => {
  const {
    getters: { userId }
  } = useContext(AuthContext);
  const eateryId = userId;

  const { pathname } = useLocation();
  const subPageDisplaying = pathname.split('/').pop();

  const {
    data: details,
    isLoading,
    isSuccess
  } = useQuery({
    queryKey: ['eatery', eateryId, 'details', 'public'],
    queryFn: () => getEateryPublicDetails(eateryId!)
  });

  const subPages = [
    ['about-us', 'About us'],
    ['vouchers', 'Vouchers'],
    ['redeem', 'Redeem'],
    ['menu', 'Menu'],
    ['reviews', 'Reviews']
  ];

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    isSuccess && (
      <VStack flex={1} bg="chowdownPurple.50" pb={10}>
        <VStack height="100%" pb={6} maxW={'4xl'} width={'100%'}>
          <Box height={40} width={'100%'} px={{ base: 0, md: 14 }}>
            <Image
              src={details.thumbnail_uri}
              alt={`${details.name}'s thumbnail image`}
              width={'100%'}
              height={'100%'}
              borderBottomRadius={{ base: '0', md: '10' }}
              fit={'cover'}
            />
          </Box>
          <Flex
            px={{ base: 6, md: 14 }}
            flexDir={{ base: 'column', md: 'row' }}
            w="100%"
            justifyContent="space-between"
            align="center"
            position={{ base: 'static', md: 'sticky' }}
            height={{ base: 'auto', md: '24' }}
            my={{ base: 4, md: 5 }}
            width={'100%'}
            bg={'chowdownPurple.50'}
            top={20}>
            <Heading as={Text} align={'center'}>
              {details.name}
            </Heading>
            <Flex
              pt={{ base: 4, md: 0 }}
              flexWrap={{ base: 'wrap', md: 'nowrap' }}
              display={'flex'}
              justifyContent={'center'}
              gap={2}
              alignItems={'center'}>
              {/* Subpage buttons */}
              {subPages.map(([route, label]) => (
                <Button
                  as={Link}
                  to={route}
                  key={route}
                  width={100}
                  colorScheme={
                    subPageDisplaying === route ? 'chowdownGray' : undefined
                  }
                  borderRadius="full">
                  {label}
                </Button>
              ))}
            </Flex>
          </Flex>
          {/* Subpages */}
          <Box width={'100%'} px={{ base: 6, md: 14 }} flex={1}>
            <Outlet />
          </Box>
        </VStack>
      </VStack>
    )
  );
};

export default MyEateryHomePage;
