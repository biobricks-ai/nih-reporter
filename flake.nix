{
  description = "NIH RePORTER BioBrick";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = import nixpkgs {
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
              pkgs.chromium
              pkgs.chromedriver
            ];
          };
      });
}
