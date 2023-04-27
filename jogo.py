import cv2
import mediapipe as mp

# solução do mediapipe tipo mão tipo mão
mp_hands = mp.solutions.hands

# função para identificada a jogada da mão
# landmarks são os pontos da mão
def jogada(hand_landmarks):
    dedos = []
    #passa os pontos das mão para um array a fim de fazer os calculos
    for landmark in hand_landmarks.landmark:
        dedos.append((landmark.x, landmark.y, landmark.z)) 

    # Calculo de separação dos dedos atráves do calculo de hipotenusa
    # dedos indicador e meio
    distancia_indicador_meio = ((dedos[8][0] - dedos[12][0])**2 +
             (dedos[8][1] - dedos[12][1])**2)**0.5
    # dedos indicador e polegar
    distancia_indicador_polegar = ((dedos[8][0] - dedos[4][0])**2 +
             (dedos[8][1] - dedos[4][1])**2)**0.5

    # Verifica se o gesto corresponde a pedra, papel ou tesoura
    if  distancia_indicador_polegar < 0.04:
        return "pedra"
    elif distancia_indicador_meio > 0.06 :
        return "tesoura"
    else:
        return "papel"

video = cv2.VideoCapture('pedra-papel-tesoura.mp4')

# configuracoes para identificar as maos
with mp_hands.Hands(
        model_complexity=0, #precisão de detecção
        min_detection_confidence=0.5, #detecção minima para ser considerado 'sucesso'
        min_tracking_confidence=0.5) as hands: #ratreio da mão ser considerado 'sucesso'

    jogada_mao_1 = None
    jogada_mao_2 = None
    ganhador = None 
    pontuacao_mao_1 = 0
    pontuacao_mao_2 = 0

    while True:
        #para pegar o frame da imagem e encerrar a tela quando o vídeo acabar
        success, img = video.read() 

        #manipulação da imagem
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        #verifica se tem mais de uma mão
        identifica_maos = results.multi_hand_landmarks
        if identifica_maos and len(identifica_maos) == 2:

            # verifica onde está a mão 1 e 2
            lugar_mao_1 = min(list(map(lambda l: l.x, identifica_maos[0].landmark)))
            lugar_mao_2 = min(list(map(lambda l: l.x, identifica_maos[1].landmark)))

            mao_1 = identifica_maos[0] if lugar_mao_1 < lugar_mao_2 else identifica_maos[1]
            mao_2 = identifica_maos[0] if lugar_mao_1 > lugar_mao_2 else identifica_maos[1]

            if (jogada(mao_2) != jogada_mao_2 or jogada(mao_1) != jogada_mao_1):

                # pegar o gesto da mao da direita
                jogada_mao_2 = jogada(mao_2)

                # pegar o gesto da mao da esquerda
                jogada_mao_1 = jogada(mao_1)

                # comparação das jogadas
                if success:
                    if jogada_mao_1 == jogada_mao_2: ganhador = 0
                    elif jogada_mao_1 == "papel" and jogada_mao_2 == "pedra": ganhador = 1
                    elif jogada_mao_1 == "papel" and jogada_mao_2 == "tesoura": ganhador = 2
                    elif jogada_mao_1 == "pedra" and jogada_mao_2 == "tesoura": ganhador = 1
                    elif jogada_mao_1 == "pedra" and jogada_mao_2 == "papel": ganhador = 2
                    elif jogada_mao_1 == "tesoura" and jogada_mao_2 == "papel": ganhador = 1
                    elif jogada_mao_1 == "tesoura" and jogada_mao_2 == "pedra": ganhador = 2
                    else: print("ERRO")
                else: success = False

                if ganhador == 1:
                    pontuacao_mao_1 += 1
                elif ganhador == 2:
                    pontuacao_mao_2 += 1

        quem_ganhou = "Empate" if ganhador == 0 else f"Mao {ganhador} venceu!"


        # cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])
        cv2.putText(img, quem_ganhou, (600, 200), cv2.FONT_HERSHEY_DUPLEX, 3, (244, 23, 254), 3)
        cv2.putText(img, str("Mao 1"), (200, 750), cv2.FONT_HERSHEY_DUPLEX, 2, (244, 23, 254), 2)
        cv2.putText(img, str("Jogada: "+jogada_mao_1), (100, 850), cv2.FONT_HERSHEY_DUPLEX, 2, (244, 23, 254), 2)
        cv2.putText(img, "Pontuacao: "+str(pontuacao_mao_1), (100, 950), cv2.FONT_HERSHEY_DUPLEX, 2, (244, 23, 254), 2)
        cv2.putText(img, str('Mao 2'), (1400, 750), cv2.FONT_HERSHEY_DUPLEX, 2, (244, 23, 254), 2)
        cv2.putText(img, str("Jogada: "+jogada_mao_2), (1300, 850), cv2.FONT_HERSHEY_DUPLEX, 2, (244, 23, 254), 2)
        cv2.putText(img, "Pontuacao: "+str(pontuacao_mao_2), (1300, 950), cv2.FONT_HERSHEY_DUPLEX, 2, (244, 23, 254), 2)

        # Definições da janela de output
        cv2.namedWindow('Hands', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Hands', 800, 400)
        cv2.imshow('Hands', img)
        if cv2.waitKey(25) & 0xFF == ord('g'): 
            break

video.release()
cv2.destroyAllWindows()       
