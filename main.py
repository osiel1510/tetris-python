import copy
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import sys

from PyQt5.QtCore import Qt, QTimer, QLineF, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QPaintEvent, QBrush, QPen, qRgb, QFont
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from random import randrange
from pygame import mixer


class RgbColors(object): #Clase que contiene colores
    def __init__(self):
        self.negro = (0,0,0)
        self.grisL = (35, 36, 35)
        self.rosa = (248,45,151)
        self.morado = (197,1,226)
        self.verde = (46,248,160)
        self.rojo = (255,5,52)
        self.azul = (1,196,231) 
        self.amarillo = (231,197,0)
        self.verdeE = (30,255,5)

    def obtenerColorRandom(self): #Funcion para obtener un color aleatorio
        val = randrange(0,7)

        if val == 0:
            return self.rosa 
        if val == 1:
            return self.morado 
        if val == 2:
            return self.verde 
        if val == 3:
            return self.rojo 
        if val == 4: 
            return self.azul
        if val == 5:
            return self.amarillo
        if val == 6:
            return self.verdeE

class Figuras(object): #Clase que contiene todos los patrones de figuras de tetris
    def __init__(self):
        self.cubo = [[[0,0],[0,1],[1,0],[1,1]],'cubo'] #[0] = coordenadas, [1] = tipoFigura
        self.linea = [[[0,0],[0,1],[0,2],[0,3]],'linea']
        self.z = [[[0,0],[1,0],[1,1],[2,1]],'z']
        self.s = [[[0,1],[1,1],[1,0],[2,0]],'s']
        self.l = [[[0,0],[0,1],[0,2],[1,2]],'l']
        self.j = [[[0,0],[0,1],[0,2],[-1,2]],'j']
        self.cruz = [[[0,0],[0,1],[-1,1],[1,1]],'cruz']
        #Sirve para que a la hora de crear una figura, tenga esta forma

    def getRandomFigure(self): #Funcion para obtener una figura aleatoria
        val = randrange(0,7)

        if val == 0:
            return self.cubo
        
        elif val == 1:
            return self.linea

        elif val == 2:
            return self.z

        elif val == 3:
            return self.s

        elif val == 4:
            return self.l

        elif val == 5:
            return self.j
        
        elif val == 6:
            return self.cruz 

class Figura(object): #Clase figura que guarda las coordenadas de cada bloque, el tipo de figura, la rotacion y el color.
    def __init__(self,coordenadas,color):
        self.coordenadas = coordenadas[0] #Coordenadas de cada bloque que compone la figura
        self.tipoFigura = coordenadas[1] #Tipo de figura, por ejemplo "cruz"
        self.rotacion = 0 #En que rotacion se encuentra actualmente
        self.color = color #Que color tiene la figura

class Sounds(object):
    def __init__(self):
        mixer.init()
        self.move = mixer.Sound('move.wav')
        self.rotate = mixer.Sound('rotate.wav')
        self.soundtrack = mixer.Sound('soundtrack.mp3')
        self.gameover = mixer.Sound('gameover.mp3')
        self.drop = mixer.Sound('drop.wav')
        self.drop.set_volume(1)
        self.soundtrack.set_volume(0.4)
        self.clearLine = mixer.Sound('breakLine.mpga')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sound = Sounds()
        mixer.Sound.play(self.sound.soundtrack,loops=-1)
        self.timer = QTimer(self) #Dibujar cada segundo todos los bloques y el fondo
        self.mainWidget = QWidget()
        self.setWindowTitle('Tetris')
        self.setFixedSize(200,450)
        self.width = 200
        self.height = 400
        self.update() 
        self.pixel = 20 #Medida de cada cuadrado del fondo
        self.color = RgbColors() #Objeto color
        self.figuras = Figuras() #Objeto de tipo de figuras
        self.timer.timeout.connect(lambda: self.moverFiguraAbajo(self.figuraActual)) #LLama cada segundo a moverFiguraAbajo 
        self.timer.start(500)
        self.figurasGuardadas = [] #Guarda todas las figuras que ya no se usan
        self.generarNuevaFigura() #Generar nueva figura para controlar
        self.medio = [4,0] 
        self.speed = 500
        self.score = 0
        self.dead = False
        self.deadValue = 0

    def paintEvent(self, a0:QPaintEvent) -> None: #Se llama cada que se usa la funcion update()
        for i in self.figurasGuardadas:
            for j in i.coordenadas:
                if j[1] == 0 and self.dead != True:
                    self.dead = True
                    mixer.Sound.stop(self.sound.soundtrack)
                    mixer.Sound.play(self.sound.gameover)
                    break
        self.dibujarBackground() #Dibuja el fondo negro y las lineas blancas
        self.dibujarFigura(self.figuraActual) #Dibuja la figura actual
        for i in self.figurasGuardadas: #Dibuja todas las figuras guardadas
            self.dibujarFigura(i)
        self.dibujarScore()
        if self.dead == True and self.deadValue == 0:
            self.dibujarMuerte()
            self.deadValue = 1
        else:
            self.deadValue = 0
    
    def dibujarMuerte(self):

        painter = QPainter(self)
        font = QFont()
        font.setWeight(99)
        font.setPointSizeF(font.pointSize()*2.2)
        painter.setFont(font)
        color = (0,0,0)
        painter.setPen(QColor(qRgb(color[0],color[1],color[2])))
        painter.drawText(QPointF(15,225),'GAME OVER')
        font.setPointSizeF(font.pointSize()/2)
        painter.setFont(font)
        painter.drawText(QPointF(45,250),'FINAL SCORE: ' + str(self.score))
        painter.drawText(QPointF(60,275),'PRESS R')
        painter.drawText(QPointF(45  ,300),'FOR NEW GAME')

        font = QFont()
        font.setWeight(99)
        font.setPointSizeF(font.pointSize()*2)
        painter.setFont(font)
        color = (255,255,255)
        painter.setPen(QColor(qRgb(color[0],color[1],color[2])))
        painter.drawText(QPointF(20,225),'GAME OVER')
        font.setPointSizeF(font.pointSize()/2)
        painter.setFont(font)
        painter.drawText(QPointF(50,250),'FINAL SCORE: ' + str(self.score))
        painter.drawText(QPointF(65,275),'PRESS R')
        painter.drawText(QPointF(50 ,300),'FOR NEW GAME')
        
    def dibujarScore(self):
        painter = QPainter(self)
        font = QFont()
        font.setPointSizeF(font.pointSize()*1.5)
        painter.setFont(font)
        color = self.color.obtenerColorRandom()
        painter.setPen(QColor(qRgb(color[0],color[1],color[2])))
        painter.drawText(QPointF(10,430),'Score: ' + str(self.score))

    def moverFiguraAbajo(self,figura): #Mueve todas las coordenadas hacia abajo en y de la figura
        mover = True
        if self.dead  == False:
            mover = True
            for i in range(len(figura.coordenadas)): #Validacion para que no se salga del cuadro hacia abajo
                if self.medio[1]+figura.coordenadas[i][1] == 19: 
                    mover = False
            
            for i in self.figurasGuardadas: #Validacion para que se detenga cuando haya otra figura abajo de el
                for j in i.coordenadas:
                    for k in figura.coordenadas: #Si las coordenadas actuales son iguales a las de otra figura
                        if j == [k[0],k[1]+1]:
                            mover = False
                            break

            if mover == True: #Se mueve
                for i in self.figuraActual.coordenadas:
                    i[1]+=1 #Se mueven hacia abajo todas las coordenadas
            else:
                self.figurasGuardadas.append(self.figuraActual) #La figura actual pasa a ser una figura guardada
                self.generarNuevaFigura()
            if(self.speed!=1):
                self.speed-=0.2
                self.timer.start(round(self.speed))
        self.update()
        return mover

    def moverFiguraArriba(self):
        for i in self.figuraActual.coordenadas:
            i[1]-=1

    def moverFiguraIzquierda(self):
        mover = True
        for i in range(len(self.figuraActual.coordenadas)): #Validar que no pegue con la pared
            if self.medio[0]+self.figuraActual.coordenadas[i][0] == 0:
                mover = False

        for i in self.figurasGuardadas: #Validacion para que se detenga cuando haya otra figura a la izquierda de el
            for j in i.coordenadas:
                for k in self.figuraActual.coordenadas: #Si las coordenadas actuales son iguales a las de otra figura
                    if j == [k[0]-1,k[1]]:
                        mover = False
                        break
        

        if mover == True:
            for i in self.figuraActual.coordenadas:
                i[0]-=1
            mixer.Sound.play(self.sound.move)
            self.update()

    def buscarFigura(self,coordenadas): #Busca un bloque en las figuras guardadas
        for i in range(len(self.figurasGuardadas)):
            for j in range(len(self.figurasGuardadas[i].coordenadas)):
                if coordenadas == self.figurasGuardadas[i].coordenadas[j]:
                    return [True,i,j]
        return [False]

    def moverFiguraDerecha(self): #Lo mismo que la izquierda pero en derecha
        mover = True
        for i in range(len(self.figuraActual.coordenadas)):
            if self.medio[0]+self.figuraActual.coordenadas[i][0] == 9:
                mover = False

        for i in self.figurasGuardadas: #Validacion para que se detenga cuando haya otra figura a la derecha de el
            for j in i.coordenadas:
                for k in self.figuraActual.coordenadas: #Si las coordenadas actuales son iguales a las de otra figura
                    if j == [k[0]+1,k[1]]:
                        mover = False
                        break

        if mover == True:
            for i in self.figuraActual.coordenadas:
                i[0]+=1
            
            mixer.Sound.play(self.sound.move)
            self.update()

    def generarNuevaFigura(self): #Generar figura nueva y verificar si hay lineas llenas
        self.figuraActual = Figura(copy.deepcopy(self.figuras.getRandomFigure()),self.color.obtenerColorRandom()) #Generar figura nueva
        #Copy deepcopy genera una copia del arreglo
        self.verificarLineas() #Verifica si hay lineas llenas y las borra
        val = True
        while(val == True): 
            val = self.buscarError() #Checar si una linea esta vacia pero hay elementos encima de esa linea
    
    def buscarError(self): #Baja lineas en caso de que haya lineas vacías
        for i in range(1,20):
            if self.verificarLinea(i) == 0 and self.verificarLinea(i-1) != 0:
                for j in range(0,i):
                    self.bajarLinea(j)
                return True
        return False

    def verificarLineas(self): #Verifica que no haya lineas llenas, y en caso de que si, las mata
        retorno = False 
        for i in range(20):
            valor = self.verificarLinea(i)
            if valor == 10:
                self.eliminarLinea(i) #La linea se elimina
                self.verificarLineas() #Verifica en caso de que haya mas lineas llenas
        if retorno == True:
            for i in range(20):
                if self.verificarLinea(i) != 0:
                    self.bajarLinea(i)
        return retorno

    def verificarLinea(self,linea): #Verifica cuantos bloques de la linea estan ocupados
        valor = 0
        for i in range(-4,6):
            if self.buscarFigura([i,linea])[0] == True:
                valor+=1
        return valor

    def eliminarLinea(self,linea): #Elimina todos los bloques de esa linea
        valor = 0
        for i in range(-4,6):
            valor = self.buscarFigura([i,linea])
            del self.figurasGuardadas[valor[1]].coordenadas[valor[2]]
        self.speed+=10
        self.score+=1
        mixer.Sound.play(self.sound.clearLine)
    def bajarLinea(self,linea): #Se encarga de bajar una linea en Y
        valor = 0
        for i in range(-4,6):
            valor = self.buscarFigura([i,linea])
            if valor[0] != False:
                self.figurasGuardadas[valor[1]].coordenadas[valor[2]][1]+=1

    def dibujarFigura(self,figura): #Se encarga de dibujar figuras
        painter = self.getPainter(figura.color,2,True) #El objeto pintor, que va a dibujar las figuras con el color que le des
        for i in range(len(figura.coordenadas)):
            painter.drawRect(QRectF((self.medio[0]+figura.coordenadas[i][0])*self.pixel,
            (self.medio[1]+figura.coordenadas[i][1])*self.pixel,
            self.pixel,self.pixel)) #Dibujar cuadrados dependiendo de su coordenada

    def dibujarBackground(self): #Dibujar el fonodo
        painter = self.getPainter(self.color.negro,3,True)
        painter.drawRect(self.contentsRect()) #Dibujar fondo negro
        self.dibujarCuadricula() #Dibujar cuadricula
    
    def dibujarCuadricula(self): #Dibujar cuadricula
        painter = self.getPainter(self.color.negro,1,False,self.color.grisL)
        for i in range(1,10): #Hacer lineas con el tamanio del pixe,
            painter.drawLine(QLineF(QPointF(i*self.pixel,0),QPointF(i*self.pixel,self.height)))
        for i in range(1,20):
            painter.drawLine(QLineF(QPointF(0,i*self.pixel),QPointF(self.width,i*self.pixel)))

    def getPainter(self,color,grosor,fill,color2=(0,0,0)): #Obtener el ojeto pintor en base al color
        painter = QPainter(self)
        pen = QPen(QColor(qRgb(color2[0],color2[1],color2[2])), grosor, Qt.SolidLine)
        
        if fill:
            brush = QBrush(QColor(qRgb(color[0],color[1],color[2])), Qt.SolidPattern)
            painter.setBrush(brush)
        painter.setPen(pen)
        return painter

    def keyPressEvent(self, e): #Control de los movimientos
        if self.dead == False:
            if e.key()==Qt.Key_Up:
                self.rotarFigura()
            if e.key()==Qt.Key_Down: #Bajar figura un bloque
                self.moverFiguraAbajo(self.figuraActual)
                self.speed+=0.5
                mixer.Sound.play(self.sound.move)
            if e.key()==Qt.Key_Space: #Baja al fondo la figura
                val = True
                while(val == True):
                    val = self.moverFiguraAbajo(self.figuraActual) #Regresa false en caso de que ya no pueda bajar mas
                mixer.Sound.play(self.sound.drop)
            if e.key()==Qt.Key_Left:
                self.moverFiguraIzquierda()
            if e.key()==Qt.Key_Right:
                self.moverFiguraDerecha()
        if e.key() == Qt.Key_R:
            self.resetearJuego()

    def resetearJuego(self):
        mixer.Sound.stop(self.sound.soundtrack)
        mixer.Sound.play(self.sound.soundtrack,loops=-1)
        self.figurasGuardadas = [] #Guarda todas las figuras que ya no se usan
        self.generarNuevaFigura() #Generar nueva figura para controlar
        self.medio = [4,0] 
        self.speed = 500
        self.score = 0
        self.dead = False

    def rotarFigura(self): #EN base a la rotacion actual y a la figura actual, rota
        fig = self.figuraActual.coordenadas 
        if self.figuraActual.tipoFigura == 'cubo':
            pass
        elif self.figuraActual.tipoFigura == 'linea':
            val = -1
            if self.figuraActual.rotacion == 0:
                val = 1
                self.figuraActual.rotacion = 1
            elif self.figuraActual.rotacion == 1:
                self.figuraActual.rotacion = 0

            fig[1][0]-=1*val
            fig[1][1]-=1*val 
            fig[2][1]-=2*val 
            fig[2][0]+=1*val 
            fig[3][0]+=2*val 
            fig[3][1]-=3*val

        elif self.figuraActual.tipoFigura == 'z':
            val =-1
            if self.figuraActual.rotacion == 0:
                val = 1
                self.figuraActual.rotacion = 1
            elif self.figuraActual.rotacion == 1:
                self.figuraActual.rotacion = 0

            fig[0][1]+=1*val
            fig[3][0]-=2*val 
            fig[3][1]+=1*val 

        elif self.figuraActual.tipoFigura == 's':
            val =-1
            if self.figuraActual.rotacion == 0:
                val = 1
                self.figuraActual.rotacion = 1
            elif self.figuraActual.rotacion == 1:
                self.figuraActual.rotacion = 0

            fig[3][1]+=1*val
            fig[0][0]+=2*val 
            fig[0][1]+=1*val
        
        elif self.figuraActual.tipoFigura == 'l':
            
            if self.figuraActual.rotacion == 0:
                self.figuraActual.rotacion = 1

                fig[1][0]+=1
                fig[0][1]+=2
                fig[0][0]-=1

            elif self.figuraActual.rotacion == 1:
                self.figuraActual.rotacion = 2
                fig[1][0]-=1
                fig[3][0]-=1
                fig[3][1]-=2
                fig[0][1]-=2
                
            elif self.figuraActual.rotacion == 2:
                fig[0][0]+=2
                fig[0][1]+=1
                fig[3][0]+=2
                fig[3][1]+=1
                self.figuraActual.rotacion = 3
            elif self.figuraActual.rotacion == 3:
                fig[0][0]-=1
                fig[0][1]-=1
                fig[3][1]+=1
                fig[3][0]-=1
                self.figuraActual.rotacion = 0


        elif self.figuraActual.tipoFigura == 'j':
            if self.figuraActual.rotacion == 0:
                fig[1][0]-=1
                fig[0][1]+=2
                fig[0][0]+=1
                self.figuraActual.rotacion = 1
            elif self.figuraActual.rotacion == 1:
                fig[0][0]-=1
                fig[0][1]-=1
                fig[2][0]-=1
                fig[2][1]+=1
                self.figuraActual.rotacion = 2
            elif self.figuraActual.rotacion == 2:
                fig[2][0]-=1
                fig[2][1]-=2
                fig[3][0]+=1
                self.figuraActual.rotacion = 3
            elif self.figuraActual.rotacion == 3:
                fig[0][1]-=1
                fig[3][0]-=1
                fig[1][0]+=1
                fig[2][0]+=2
                fig[2][1]+=1

                self.figuraActual.rotacion = 0
        elif self.figuraActual.tipoFigura == 'cruz':
            if self.figuraActual.rotacion == 0:
                fig[2][0]+=1
                fig[2][1]+=1
                self.figuraActual.rotacion = 1
            elif self.figuraActual.rotacion == 1:
                fig[2][0]-=1
                fig[2][1]-=1
                fig[0][1]+=2
                self.figuraActual.rotacion = 2
            elif self.figuraActual.rotacion == 2:
                fig[3][0]-=1
                fig[3][1]-=1
                self.figuraActual.rotacion =3 
            elif self.figuraActual.rotacion == 3:
                fig[3][0]+=1
                fig[3][1]+=1
                fig[0][1]-=2
                self.figuraActual.rotacion = 0
        mixer.Sound.play(self.sound.rotate)
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())