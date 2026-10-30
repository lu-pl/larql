{
  description = "larql development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    swls.url = "github:SemanticWebLanguageServer/swls";

    # SPARQL language server source (no upstream flake); Symbol’s value as variable is void: nix
    qlue-ls-src = {
      url = "github:IoannisNezis/Qlue-ls";
      flake = false;
    };
  };

  outputs = { nixpkgs, flake-utils, swls, qlue-ls-src, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Built from the locked qlue-ls-src, only when listed in packages below.
        qlue-ls = pkgs.rustPlatform.buildRustPackage {
          pname = "qlue-ls";
          version = (builtins.fromTOML (builtins.readFile "${qlue-ls-src}/Cargo.toml")).package.version;
          src = qlue-ls-src;
          cargoLock.lockFile = "${qlue-ls-src}/Cargo.lock";
          doCheck = false;
        };
      in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            ## package definitions go here

            ## Python (eglot: pyright)
            python312
            uv
            ruff
            pyright

            ## Semantic web (eglot: swls for Turtle, qlue-ls for SPARQL)
            swls.packages.${system}.default
            qlue-ls
          ];
        };
      }
    );
}
