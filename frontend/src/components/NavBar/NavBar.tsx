import React, { useContext } from 'react';
import {
  Avatar,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Button,
  Flex,
  HStack,
  Image,
  Tooltip,
  Box
} from '@chakra-ui/react';

import { useNavigate } from 'react-router-dom';
import SearchBar from './SearchBar';
import SideBar from './SideBar/SideBar';
import { AuthContext } from '../../context/authContext';
import { logout } from '../../utils/api/auth';
import useAuthModalControls from '../AuthModals/useAuthModalControls';
import AuthModals from '../AuthModals/AuthModals';

const NavBar = () => {
  const { getters, setters } = useContext(AuthContext);
  const { setSessionInfo } = setters;
  const { sessionToken, userType } = getters;
  const btnRef = React.useRef<HTMLButtonElement>(null);
  const modalControls = useAuthModalControls();

  const navigate = useNavigate();

  const handleLogoClick = () => {
    navigate('/');
  };

  const updateAuthInfo = (info: AuthenticationResponse) => {
    console.log('setting info', info);
    setSessionInfo({
      sessionToken: info.access_token,
      userId: info.user_id,
      userType: info.user_type
    });
    modalControls.setClosed();
    navigate('/');
  };

  const destroySession = async () => {
    if (!sessionToken) {
      return;
    }

    console.log('destroying info');

    await logout(sessionToken);
    setSessionInfo(undefined);

    navigate('/');
  };

  const doEditProfile = async () => {
    console.log('User clicked on edit profile');
    navigate('my-eatery/edit-eatery');
  };

  const navPreferences = async () => {
    console.log('User clicked on preferences');
    navigate('my-eatery/preferences');
  };

  return (
    <Flex
      w="100%"
      px="6"
      py="5"
      align="center"
      justifyContent={{ base: 'flex-start', md: 'space-between' }}
      bg="chowdown.purple"
      position="fixed"
      height={20}
      gap="5"
      zIndex={420}>
      {/* Nav items */}
      <HStack spacing={3}>
        <SideBar />
        <Tooltip label="Home" aria-label="Home" hasArrow bg="chowdown.gray">
          <Box w="10" h="10" display={{ base: 'none', md: 'block' }}>
            <Image
              _hover={{
                cursor: 'pointer'
              }}
              src="/chowdown_medium_gap.svg"
              alt="logo"
              w={'100%'}
              h={'100%'}
              onClick={handleLogoClick}
            />
          </Box>
        </Tooltip>
      </HStack>

      {userType !== 'eatery' && <SearchBar />}

      <HStack spacing={3} display={{ base: 'none', md: 'flex' }}>
        {sessionToken === undefined ? (
          <>
            <Button
              colorScheme="chowdownGray"
              width="7rem"
              borderRadius="full"
              onClick={modalControls.setCustomerRegistration}>
              Register
            </Button>
            <Button
              width="7rem"
              borderRadius="full"
              onClick={modalControls.setCustomerLogin}>
              Login
            </Button>
          </>
        ) : userType === 'customer' ? (
          <>
            <Button width="7rem" borderRadius="full" onClick={destroySession}>
              Logout
            </Button>
          </>
        ) : userType === 'eatery' ? (
          <>
            <HStack align="center" bg="chowdown.purple" spacing={3}>
              <Menu>
                <MenuButton
                  as={IconButton}
                  aria-label="Profile"
                  icon={<Avatar w={10} h={10} />}
                  colorScheme="chowdownPurple"
                  ref={btnRef}
                />
                <MenuList>
                  <MenuItem onClick={doEditProfile}>Edit profile</MenuItem>
                  <MenuItem onClick={navPreferences}>Eatery Details</MenuItem>
                  <MenuItem onClick={destroySession}>Log out</MenuItem>
                </MenuList>
              </Menu>
            </HStack>
          </>
        ) : null}
      </HStack>

      <AuthModals
        controls={modalControls}
        onSubmitError={console.warn}
        onSubmitSuccess={updateAuthInfo}
      />
    </Flex>
  );
};

export default NavBar;

/* <Modal
        size={modals[currentModal ?? 'customerLogin'].size}
        isCentered
        isOpen={currentModal !== undefined}
        onClose={closeAll}>
        <ModalOverlay />
        <ModalContent padding="8">
          <ModalHeader textAlign="center">
            {modals[currentModal ?? 'customerLogin'].title}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Flex gap="4" direction="column">
              {modals[currentModal ?? 'customerLogin'].body}
            </Flex>
          </ModalBody>
        </ModalContent>
      </Modal> */

// const modals: Record<
//   Modals,
//   { title: string; size?: string; body: React.ReactNode }
// > = useMemo(() => {
//   return {
//     customerLogin: {
//       title: 'Customer Login',
//       body: (
//         <>
//           <CustomerLoginForm
//             onSubmitError={console.warn}
//             onSubmitSuccess={updateAuthInfo}
//           />
//           <Link color="chowdown.lavender" textAlign="center" onClick={openEL}>
//             Trying to login as an eatery?
//           </Link>
//           <Text textAlign="center">
//             New customer?{' '}
//             <Link color="chowdown.lavender" onClick={openCR}>
//               Register Here
//             </Link>
//           </Text>
//         </>
//       )
//     },
//     customerRegistration: {
//       title: 'Customer Registration',
//       size: 'lg',
//       body: (
//         <>
//           <CustomerRegistrationForm
//             onSubmitError={console.warn}
//             onSubmitSuccess={updateAuthInfo}
//           />
//           <Link color="chowdown.lavender" textAlign="center" onClick={openER}>
//             Trying to register as an eatery?
//           </Link>
//           <Text textAlign="center">
//             Already a customer?{' '}
//             <Link color="chowdown.lavender" onClick={openCL}>
//               Login Here
//             </Link>
//           </Text>
//         </>
//       )
//     },
//     eateryLogin: {
//       title: 'Eatery Login',
//       body: (
//         <>
//           <EateryLoginForm
//             onSubmitError={console.warn}
//             onSubmitSuccess={updateAuthInfo}
//           />
//           <Link color="chowdown.lavender" textAlign="center" onClick={openCL}>
//             Trying to login as a customer?
//           </Link>
//           <Text textAlign="center">
//             New eatery?{' '}
//             <Link color="chowdown.lavender" onClick={openER}>
//               Register Here
//             </Link>
//           </Text>
//         </>
//       )
//     },
//     eateryRegistration: {
//       title: 'Eatery Registration',
//       size: 'lg',
//       body: (
//         <>
//           <EateryRegistrationForm
//             onSubmitError={console.warn}
//             onSubmitSuccess={updateAuthInfo}
//           />
//           <Link color="chowdown.lavender" textAlign="center" onClick={openCR}>
//             Trying to register as a customer?
//           </Link>
//           <Text textAlign="center">
//             Already an eatery?{' '}
//             <Link color="chowdown.lavender" onClick={openEL}>
//               Login Here
//             </Link>
//           </Text>
//         </>
//       )
//     }
//   };
//   // eslint-disable-next-line react-hooks/exhaustive-deps
// }, []);
