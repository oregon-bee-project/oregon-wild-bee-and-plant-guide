import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { act } from 'react';
import { expect } from 'vitest';
import { Provider } from "@/components/ui/provider"
import App from './App';

describe('App component', () => {
  test('renders the header', () => {
    render(
      <Provider>
        <App />
      </Provider>
    );

    expect(screen.getByText(/oregon bee atlas/i)).toBeInTheDocument();
  });

  test.skip('renders the prompt sidebar', () => {
    render(
      <Provider>
        <App />
      </Provider>
    );

    // check for sidebar title
    expect(screen.getByText(/prompt sidebar/i)).toBeInTheDocument();

    // check for both segments of the segment control
    const mapOption = screen.getByRole('radio', { name: /map page/i });
    const resultsOption = screen.getByRole('radio', { name: /results page/i });
    expect(mapOption).toBeInTheDocument();
    expect(resultsOption).toBeInTheDocument();
  });

  test.skip('renders the map page', () => {
    render(
      <Provider>
        <App />
      </Provider>
    );

    // check that map page option is selected
    expect(screen.getByRole('radio', { name: /map page/i })).toBeChecked();

    // check that map is present
    const mapContainer = document.getElementById('map');
    expect(mapContainer).toBeInTheDocument();
  
  });

  test.skip('renders the results page', async () => {
    render(
      <Provider>
        <App />
      </Provider>
    );

    // target "results page" option, expect it to not be selected at first
    const resultsOption = screen.getByRole('radio', { name: /results page/i });
    expect(resultsOption).not.toBeChecked();

    // click on results page
    await act(async () => {
      await userEvent.click(resultsOption);
    });

    // should be checked
    expect(resultsOption).toBeChecked();

    // check that data/results placeholder message is present
    expect(screen.getByText(/data\/results displayed here/i)).toBeInTheDocument();
  });

});