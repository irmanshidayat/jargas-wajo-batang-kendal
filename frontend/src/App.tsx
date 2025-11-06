import { RouterProvider } from 'react-router-dom'
import { Provider } from 'react-redux'
import { store } from './store/store'
import { router } from './routes/routes'
import ErrorBoundary from './components/common/ErrorBoundary'
import './styles/globals.css'

function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
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
