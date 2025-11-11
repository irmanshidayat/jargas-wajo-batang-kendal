import { useEffect } from 'react'
import { RouterProvider } from 'react-router-dom'
import { Provider, useDispatch } from 'react-redux'
import type { AppDispatch } from './store/store'
import { store } from './store/store'
import { router } from './routes/routes'
import ErrorBoundary from './components/common/ErrorBoundary'
import { validateToken } from './store/slices/authSlice'
import './styles/globals.css'

/**
 * Component untuk validate token saat app load
 * Hanya validate sekali saat component mount
 */
const TokenValidator = () => {
  const dispatch = useDispatch<AppDispatch>()

  useEffect(() => {
    // Check apakah ada token di localStorage
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')

    // Hanya validate jika ada token DAN user
    // Jika tidak ada, biarkan user login dulu
    if (token && user) {
      // Validate token dengan fetch user profile
      // Redux akan handle deduplication jika dipanggil berulang
      dispatch(validateToken())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    // Hanya run sekali saat mount, tidak perlu re-run saat dispatch berubah
  }, [])

  return null
}

function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <TokenValidator />
        <RouterProvider 
          router={router}
          future={{
            v7_startTransition: true,
          }}
        />
      </Provider>
    </ErrorBoundary>
  )
}

export default App
