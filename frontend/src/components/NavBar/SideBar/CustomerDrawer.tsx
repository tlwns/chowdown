import {
  Button,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerOverlay,
  VStack
} from '@chakra-ui/react';
import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../../context/authContext';
import { logout } from '../../../utils/api/auth';

type CustomerDrawerProps = {
  isOpen: boolean;
  onClose: () => void;
  btnRef: React.RefObject<HTMLButtonElement>;
};

const CustomerDrawer: React.FC<CustomerDrawerProps> = ({
  isOpen,
  onClose,
  btnRef
}) => {
  const { getters, setters } = useContext(AuthContext);
  const { setSessionInfo } = setters;
  const { sessionToken } = getters;
  const navigate = useNavigate();

  const destroySession = async () => {
    if (!sessionToken) {
      return;
    }

    console.log('destroying info');

    await logout(sessionToken);
    setSessionInfo(undefined);

    navigate('/');
  };

  return (
    <Drawer
      isOpen={isOpen}
      placement="left"
      onClose={onClose}
      finalFocusRef={btnRef}>
      <DrawerOverlay />
      <DrawerContent
        bg="chowdown.lavender"
        textColor="white"
        borderRightRadius="lg">
        <DrawerCloseButton size="lg" />
        <DrawerBody>
          <VStack
            alignItems="flex-start"
            justifyContent="center"
            height="100%"
            gap="10">
            <Button
              as={Link}
              to="/"
              onClick={onClose}
              variant="link"
              fontSize={'lg'}
              textColor="inherit">
              Home
            </Button>
            <Button
              as={Link}
              to="customer/my-account"
              fontSize={'lg'}
              textColor="inherit"
              variant="link">
              Account
            </Button>
            <Button
              as={Link}
              to="/customer/my-vouchers"
              fontSize={'lg'}
              textColor="inherit"
              onClick={onClose}
              variant="link">
              My Vouchers
            </Button>
            <Button
              variant="link"
              fontSize={'lg'}
              textColor="inherit"
              onClick={() => {
                onClose();
                destroySession();
              }}>
              Logout
            </Button>
          </VStack>
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  );
};

export default CustomerDrawer;
