import {
  Button,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerOverlay,
  VStack
} from '@chakra-ui/react';
import React from 'react';
import useAuthModalControls from '../../AuthModals/useAuthModalControls';
import AuthModals from '../../AuthModals/AuthModals';
import { useContext } from 'react';
import { AuthContext } from '../../../context/authContext';

type UserDrawerProps = {
  isOpen: boolean;
  onClose: () => void;
  btnRef: React.RefObject<HTMLButtonElement>;
};

const UserDrawer: React.FC<UserDrawerProps> = ({ isOpen, onClose, btnRef }) => {
  const { setters } = useContext(AuthContext);
  const { setSessionInfo } = setters;

  const modalControls = useAuthModalControls();

  const updateAuthInfo = (info: AuthenticationResponse) => {
    console.log('setting info', info);
    setSessionInfo({
      sessionToken: info.access_token,
      userId: info.user_id,
      userType: info.user_type
    });
    modalControls.setClosed();
  };

  return (
    <>
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
                variant="link"
                fontSize={'lg'}
                textColor="inherit"
                onClick={modalControls.setCustomerLogin}>
                Register/Login
              </Button>
              <Button variant="link" fontSize={'lg'} textColor="inherit">
                Help
              </Button>
              <Button variant="link" fontSize={'lg'} textColor="inherit">
                About us
              </Button>
              <Button
                variant="link"
                fontSize={'lg'}
                textColor="inherit"
                onClick={modalControls.setEateryRegistration}>
                Register your eatery
              </Button>
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
      <AuthModals
        controls={modalControls}
        onSubmitError={console.warn}
        onSubmitSuccess={updateAuthInfo}
      />
    </>
  );
};

export default UserDrawer;
