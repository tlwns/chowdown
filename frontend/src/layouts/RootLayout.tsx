import { Outlet } from 'react-router-dom';
import { Flex } from '@chakra-ui/react';

import React from 'react';
import NavBar from '../components/NavBar/NavBar';

const RootLayout: React.FC = () => {
  return (
    <>
      <Flex flexDir={'column'} height={'100svh'}>
        <NavBar />
        <Flex mt="20" flex={1}>
          <Outlet />
        </Flex>
      </Flex>
    </>
  );
};

export default RootLayout;
