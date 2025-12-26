{
  description = "git commit-msg hook enforcing conventional commit syntax";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    fp.url = "github:hercules-ci/flake-parts";
    devshell = {
      url = "github:numtide/devshell";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs:
    let
      projectName = "conventional-msg";
    in
    inputs.fp.lib.mkFlake { inherit inputs; } {
      systems = inputs.nixpkgs.lib.systems.flakeExposed;
      perSystem = { system, pkgs, lib, ... }: {
        _module.args.pkgs = import inputs.nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [
            inputs.devshell.overlays.default
          ];
        };
        devShells.default = pkgs.devshell.mkShell {
          name = "${projectName}";
          motd = "{32}${projectName} activated{reset}\n$(type -p menu &>/dev/null && menu)\n";

          env = [
            {
              name = "LD_LIBRARY_PATH" ;
              value = pkgs.lib.makeLibraryPath [
                pkgs.file
                pkgs.stdenv.cc.cc.lib
              ];
            }
          ];

          packages = with pkgs; [
            (python313.withPackages (
              pypkgs: with pypkgs; [
                pip
                isort
              ]
            ))
            gh
            poetry
            pre-commit
            pyright
            ruff
          ];

          commands = [
            {
              name = "format";
              command = ''
              pushd $PRJ_ROOT;
              (ruff format -q ${projectName}/ && isort -q --dt ${projectName}/);
              popd'';
              help = "apply ruff, isort formatting";
            }

            {
              name = "check";
              command = ''
              pushd $PRJ_ROOT;
              echo "${projectName}"
              (ruff check ${projectName}/ || true);
              pyright ${projectName}/;
              popd'';
              help = "run ruff linter, pyright type checker";
            }
          ];
        };
      };
    };
}
