# Resolve Autopilot

Automatize o **DaVinci Resolve Studio** com Python e [Claude Code](https://claude.com/claude-code):
monte a timeline a partir de uma pasta de takes, aplique um visual consistente, pré-misture o áudio
(voz tratada, música que abaixa quando há fala, efeitos sonoros nos cortes) e renderize.

Deixe rodando e revise o resultado de manhã. A mídia original nunca é alterada nem apagada.

🇺🇸 [Read in English](README.md)

## O que tem

- **Conexão** com o Resolve no Windows, macOS e Linux, com mensagem clara quando ele não responde.
- **Montagem da timeline** a partir de takes numerados (`01.mp4`, `02.mp4`...).
- **Visual**: zoom alternado e cor (CDL) numa timeline *duplicada*, com marcador em cada corte.
- **Pré-mix de áudio com ffmpeg** (a API não controla volume): voz reconstruída dos originais e limpa,
  música com ducking, efeitos alinhados ao corte, tudo no volume-alvo (LUFS).
- **Render** pela fila do Resolve, aplicando as configurações uma a uma.
- **Inspetor somente leitura** que mostra as timelines em JSON para o assistente de IA.
- **Skill do Claude Code** em `skills/resolve-autopilot`.

## Requisitos

- DaVinci Resolve **Studio** aberto com um projeto.
- Resolve: *Preferences > System > General > External scripting using: Local*.
- Python 3.9+ e [ffmpeg](https://ffmpeg.org/) (ou `pip install imageio-ffmpeg`).

## Instalar e usar

```bash
git clone https://github.com/costagonzaga/resolve-autopilot
cd resolve-autopilot
pip install -e ".[ffmpeg]"
resolve-autopilot check
resolve-autopilot build ./takes "Meu reel"
resolve-autopilot look "Meu reel" "Meu reel v2"
resolve-autopilot mix "Meu reel v2" musica.wav ./audio --sfx whoosh1.wav whoosh2.wav
resolve-autopilot add-audio "Meu reel v2" ./audio
resolve-autopilot render "Meu reel v2" ./saida reel --size 1080 1920
```

## Situação

Versão inicial (v0.1), testada no Windows com Resolve Studio 21. Os caminhos de macOS e Linux seguem
a documentação da Blackmagic, mas **não foram testados**: relatos e correções são bem-vindos.
Veja o [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

MIT. DaVinci Resolve é marca da Blackmagic Design; este projeto não tem ligação com ela.
