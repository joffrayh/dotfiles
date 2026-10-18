clean() {
  sudo paccache -r # cleans package cache, keeping the 3 most recent versions

  # remove any existing orphan packages 
  orphans=$(paru -Qtdq)

  if [ -n "$orphans" ]; then
    paru -Rns $orphans
  else
    echo "No orphan packages found."
  fi
}

clean