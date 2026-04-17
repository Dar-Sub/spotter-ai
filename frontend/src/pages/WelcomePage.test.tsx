import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { WelcomePage } from "./WelcomePage";

describe("WelcomePage", () => {
  it("renders headline and link to planner", () => {
    render(
      <MemoryRouter>
        <Routes>
          <Route path="/" element={<WelcomePage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /continue to planner/i })).toHaveAttribute("href", "/planner");
  });
});
