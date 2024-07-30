import { HamburgerIcon } from '@chakra-ui/icons';
import { IconButton, useDisclosure } from '@chakra-ui/react';

import React, { useContext } from 'react';

import CustomerDrawer from './CustomerDrawer';
import EateryDrawer from './EateryDrawer';
import UserDrawer from './UserDrawer';
import { AuthContext } from '../../../context/authContext';

const SideBar = () => {
  const { getters } = useContext(AuthContext);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const btnRef = React.useRef<HTMLButtonElement>(null);

  return (
    <>
      <IconButton
        aria-label="Open sidebar"
        icon={<HamburgerIcon w={7} h={7} />}
        colorScheme="chowdownPurple"
        onClick={onOpen}
        ref={btnRef}
      />
      {getters.sessionToken === undefined ? (
        <UserDrawer isOpen={isOpen} onClose={onClose} btnRef={btnRef} />
      ) : getters.userType === 'customer' ? (
        <CustomerDrawer isOpen={isOpen} onClose={onClose} btnRef={btnRef} />
      ) : (
        <EateryDrawer isOpen={isOpen} onClose={onClose} btnRef={btnRef} />
      )}
    </>
  );
};

export default SideBar;
