import {
  Button,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerOverlay,
  VStack
} from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import React from 'react';
import { useContext } from 'react';
import { AuthContext } from '../../../context/authContext';
import { logout } from '../../../utils/api/auth';
import { useNavigate } from 'react-router-dom';

type EateryDrawerProps = {
  isOpen: boolean;
  onClose: () => void;
  btnRef: React.RefObject<HTMLButtonElement>;
};

const EateryDrawer: React.FC<EateryDrawerProps> = ({
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
              to={'/'}
              onClick={onClose}
              variant="link"
              fontSize={'lg'}
              textColor="inherit">
              My Eatery
            </Button>
            <Button
              as={Link}
              to={'/my-eatery/edit-eatery'}
              onClick={onClose}
              variant="link"
              fontSize={'lg'}
              textColor="inherit">
              Edit Eatery
            </Button>
            <Button
              as={Link}
              to={'/my-eatery/preferences'}
              onClick={onClose}
              variant="link"
              fontSize={'lg'}
              textColor="inherit">
              Eatery Details
            </Button>
            <Button
              onClick={() => {
                onClose();
                destroySession();
              }}
              variant="link"
              fontSize={'lg'}
              textColor="inherit">
              Logout
            </Button>
          </VStack>
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  );
};

export default EateryDrawer;
