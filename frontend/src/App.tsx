import React, { useContext, useMemo } from 'react';
import {
  Navigate,
  Route,
  RouterProvider,
  createBrowserRouter,
  createRoutesFromElements
} from 'react-router-dom';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import RootLayout from './layouts/RootLayout';
import ThemingPlayground from './pages/ThemingPlayground';

import MyEateryHomePage from './pages/MyEateryHomePage/MyEateryHomePage';
import MyAboutUsSubPage from './pages/MyEateryHomePage/SubPages/AboutUsSubPage';
import MyMenuSubPage from './pages/MyEateryHomePage/SubPages/MenuSubPage';
import MyReviewsSubPage from './pages/MyEateryHomePage/SubPages/ReviewsSubPage';
import MyVouchersSubPage from './pages/MyEateryHomePage/SubPages/VouchersSubPage';
import MyRedemptionSubPage from './pages/MyEateryHomePage/SubPages/RedemptionSubPage';

import CustomerHomePage from './pages/Customer/CustomerHomePage';
import MyAccountPage from './pages/Customer/MyAccountPage';
import MyVouchersPage from './pages/Customer/MyVouchersPage';
import EateryPage from './pages/EateryPage/EateryPage';
import AboutUsSubPage from './pages/EateryPage/SubPages/AboutUsSubPage';
import MenuSubPage from './pages/EateryPage/SubPages/MenuSubPage';
import ReviewsSubPage from './pages/EateryPage/SubPages/ReviewsSubPage';
import VouchersSubPage from './pages/EateryPage/SubPages/VouchersSubPage';
import EateryPreferencesSubPage from './pages/MyEateryHomePage/SubPages/EateryPreferencesSubpage';
import EditEaterySubPage from './pages/MyEateryHomePage/SubPages/EditEaterySubPage';
import NotifsSubPage from './pages/MyEateryHomePage/SubPages/NotifsSubPage';
import PageNotFoundPage from './pages/PageNotFoundPage';

import { ZodError } from 'zod';
import SearchPage from './pages/SearchPage';
import { AuthContext } from './context/authContext';
import UserHomePage from './pages/UserHomePage';
import CurrentVouchersSubPage from './pages/Customer/CurrentVouchersSubPage';
import PastVouchersSubPage from './pages/Customer/PastVouchersSubPage';
import { AxiosError } from 'axios';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, err) => {
        if (err instanceof ZodError) {
          return false;
        }
        return failureCount < 3;
      },
      throwOnError: true
    },
    mutations: {
      retry: false,
      throwOnError: (err) => !(err instanceof AxiosError)
    }
  }
});

const App: React.FC = () => {
  const {
    getters: { userType }
  } = useContext(AuthContext);

  const router = useMemo(
    () =>
      createBrowserRouter(
        createRoutesFromElements(
          <>
            <Route path="/" element={<RootLayout />}>
              {userType === undefined && (
                <>
                  <Route
                    index
                    element={<Navigate to="home" replace={true} />}
                  />
                  <Route path="home" element={<UserHomePage />} />
                  <Route path="eatery/:eateryId" element={<EateryPage />}>
                    <Route
                      index
                      element={<Navigate to="vouchers" replace={true} />}
                    />
                    <Route path="vouchers" element={<VouchersSubPage />} />
                    <Route path="about-us" element={<AboutUsSubPage />} />
                    <Route path="menu" element={<MenuSubPage />} />
                    <Route path="reviews" element={<ReviewsSubPage />} />
                  </Route>
                </>
              )}
              {userType === 'eatery' && (
                <>
                  <Route
                    index
                    element={<Navigate to="my-eatery" replace={true} />}
                  />
                  <Route path="my-eatery">
                    <Route
                      index
                      element={<Navigate to="home" replace={true} />}
                    />
                    <Route path="home" element={<MyEateryHomePage />}>
                      <Route
                        index
                        element={<Navigate to="vouchers" replace={true} />}
                      />
                      <Route path="vouchers" element={<MyVouchersSubPage />} />
                      <Route path="about-us" element={<MyAboutUsSubPage />} />
                      <Route path="menu" element={<MyMenuSubPage />} />
                      <Route path="reviews" element={<MyReviewsSubPage />} />
                      <Route path="redeem" element={<MyRedemptionSubPage />} />
                    </Route>
                    <Route path="edit-eatery" element={<EditEaterySubPage />} />
                    <Route
                      path="preferences"
                      element={<EateryPreferencesSubPage />}
                    />
                    <Route path="notifications" element={<NotifsSubPage />} />
                  </Route>
                </>
              )}
              {userType === 'customer' && (
                <>
                  <Route
                    index
                    element={<Navigate to="customer" replace={true} />}
                  />
                  <Route path="customer" element={<CustomerHomePage />} />
                  <Route
                    path="customer/my-account"
                    element={<MyAccountPage />}
                  />
                  <Route
                    path="customer/my-vouchers"
                    element={<MyVouchersPage />}>
                    <Route index element={<CurrentVouchersSubPage />} />
                    <Route
                      path="past-vouchers"
                      element={<PastVouchersSubPage />}
                    />
                  </Route>
                  <Route path="eatery/:eateryId" element={<EateryPage />}>
                    <Route
                      index
                      element={<Navigate to="vouchers" replace={true} />}
                    />
                    <Route path="vouchers" element={<VouchersSubPage />} />
                    <Route path="about-us" element={<AboutUsSubPage />} />
                    <Route path="menu" element={<MenuSubPage />} />
                    <Route path="reviews" element={<ReviewsSubPage />} />
                  </Route>
                </>
              )}
              <Route path="theming" element={<ThemingPlayground />} />
              <Route path="search" element={<SearchPage />} />
            </Route>
            <Route path="*" element={<PageNotFoundPage />} />
          </>
        )
      ),
    [userType]
  );

  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
};

export default App;
