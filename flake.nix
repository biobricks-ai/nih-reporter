{
  description = "NIH RePORTER BioBrick";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
    nixpkgs-2411.url = "github:nixos/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
    dev-shell = {
      url = "github:biobricks-ai/dev-shell";
      inputs.flake-utils.follows = "flake-utils";
      inputs.nixpkgs.follows = "nixpkgs-2411";
    };
  };

  outputs = { self, nixpkgs, nixpkgs-2411, flake-utils, dev-shell }:
    flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = import nixpkgs {
            inherit system;
          };
          pkgs-2411 = import nixpkgs-2411 {
            inherit system;
          };
      in {
        devShells.default =
          let
            python3PackageOverrides = pkgs.callPackage ./maint/nixpkg/python3/packages.nix { };
            python3 = pkgs.python3.override { packageOverrides = python3PackageOverrides; };
          in pkgs.mkShell {
            buildInputs = [
              (python3.withPackages (ps: with ps; [ selenium webdriver-manager tqdm pandas pyarrow ]))
              (with pkgs; [ chromium chromedriver ])
              (with pkgs-2411; [ recode parallel coreutils gettext ])
              # Use duckdb from dev-shell
              dev-shell.packages.${system}.duckdb
            ];
          };
      });
}
